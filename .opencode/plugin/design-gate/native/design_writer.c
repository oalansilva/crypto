#define _GNU_SOURCE

#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/if_alg.h>
#include <linux/openat2.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define MAX_PATH_BYTES 16384U
#define MAX_CONTENT_BYTES (32ULL * 1024ULL * 1024ULL)
#ifndef DESIGN_BUILD_ID
#error "DESIGN_BUILD_ID is required"
#endif
#ifndef DESIGN_PROTOCOL_VERSION
#error "DESIGN_PROTOCOL_VERSION is required"
#endif

static int read_full(int fd, void *buffer, size_t length) {
  unsigned char *cursor = buffer;
  while (length > 0) {
    ssize_t count = read(fd, cursor, length);
    if (count == 0) return -1;
    if (count < 0) {
      if (errno == EINTR) continue;
      return -1;
    }
    cursor += (size_t)count;
    length -= (size_t)count;
  }
  return 0;
}

static uint64_t decode_u64(const unsigned char input[8]) {
  uint64_t value = 0;
  for (int index = 0; index < 8; index++) value = (value << 8) | input[index];
  return value;
}

static void digest_hex(const unsigned char digest[32], char output[65]) {
  for (int index = 0; index < 32; index++) sprintf(output + (index * 2), "%02x", digest[index]);
  output[64] = '\0';
}

static int sha256_fd(int fd, char output[65]) {
  int algorithm_fd = -1;
  int operation_fd = -1;
  struct sockaddr_alg address = {
      .salg_family = AF_ALG,
      .salg_type = "hash",
      .salg_name = "sha256",
  };
  unsigned char digest[32];
  unsigned char buffer[32768];
  if (lseek(fd, 0, SEEK_SET) < 0) return -1;
  algorithm_fd = socket(AF_ALG, SOCK_SEQPACKET | SOCK_CLOEXEC, 0);
  if (algorithm_fd < 0 || bind(algorithm_fd, (struct sockaddr *)&address, sizeof(address)) < 0) goto failure;
  operation_fd = accept4(algorithm_fd, NULL, 0, SOCK_CLOEXEC);
  if (operation_fd < 0) goto failure;
  for (;;) {
    ssize_t count = read(fd, buffer, sizeof(buffer));
    if (count == 0) break;
    if (count < 0) {
      if (errno == EINTR) continue;
      return -1;
    }
    size_t written = 0;
    while (written < (size_t)count) {
      ssize_t sent = write(operation_fd, buffer + written, (size_t)count - written);
      if (sent < 0) {
        if (errno == EINTR) continue;
        goto failure;
      }
      written += (size_t)sent;
    }
  }
  if (read_full(operation_fd, digest, sizeof(digest)) < 0) goto failure;
  digest_hex(digest, output);
  close(operation_fd);
  close(algorithm_fd);
  return 0;

failure:
  if (operation_fd >= 0) close(operation_fd);
  if (algorithm_fd >= 0) close(algorithm_fd);
  return -1;
}

static int valid_relative_path(const char *value) {
  if (!value[0] || value[0] == '/') return 0;
  const char *segment = value;
  while (*segment) {
    const char *slash = strchr(segment, '/');
    size_t length = slash ? (size_t)(slash - segment) : strlen(segment);
    if (length == 0 || (length == 1 && segment[0] == '.') ||
        (length == 2 && segment[0] == '.' && segment[1] == '.')) return 0;
    if (!slash) break;
    segment = slash + 1;
  }
  return 1;
}

static int open_parent_beneath(int root_fd, const char *parent) {
  if (!parent[0] || strcmp(parent, ".") == 0) return dup(root_fd);
  struct open_how how = {
      .flags = O_RDONLY | O_DIRECTORY | O_CLOEXEC,
      .resolve = RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS | RESOLVE_NO_MAGICLINKS,
  };
  return (int)syscall(SYS_openat2, root_fd, parent, &how, sizeof(how));
}

static int verify_regular_stat(const struct stat *status) {
  return S_ISREG(status->st_mode) && status->st_uid == getuid() && status->st_nlink == 1;
}

static int fail(const char *message) {
  fprintf(stderr, "design-writer: %s: %s\n", message, strerror(errno));
  return 1;
}

int main(void) {
  unsigned char header[24];
  if (read_full(STDIN_FILENO, header, sizeof(header)) < 0) return fail("incomplete protocol header");
  if (memcmp(header, "DGW1", 4) != 0) {
    errno = EPROTO;
    return fail("invalid protocol magic");
  }

  uint32_t root_length_net, path_length_net, base_length_net;
  memcpy(&root_length_net, header + 4, 4);
  memcpy(&path_length_net, header + 8, 4);
  memcpy(&base_length_net, header + 12, 4);
  uint32_t root_length = ntohl(root_length_net);
  uint32_t path_length = ntohl(path_length_net);
  uint32_t base_length = ntohl(base_length_net);
  uint64_t content_length = decode_u64(header + 16);
  if (!root_length || root_length > MAX_PATH_BYTES || !path_length || path_length > MAX_PATH_BYTES ||
      (base_length != 1 && base_length != 64) || content_length > MAX_CONTENT_BYTES) {
    errno = E2BIG;
    return fail("invalid protocol lengths");
  }

  char *root = calloc(root_length + 1, 1);
  char *relative = calloc(path_length + 1, 1);
  char *expected_base = calloc(base_length + 1, 1);
  unsigned char *content = malloc(content_length ? (size_t)content_length : 1);
  if (!root || !relative || !expected_base || !content) return fail("allocation failed");
  if (read_full(STDIN_FILENO, root, root_length) < 0 || read_full(STDIN_FILENO, relative, path_length) < 0 ||
      read_full(STDIN_FILENO, expected_base, base_length) < 0 ||
      (content_length && read_full(STDIN_FILENO, content, (size_t)content_length) < 0)) {
    return fail("incomplete protocol payload");
  }
  if (root[0] != '/' || !valid_relative_path(relative)) {
    errno = EINVAL;
    return fail("invalid root or relative path");
  }

  char *path_copy = strdup(relative);
  char *slash = strrchr(path_copy, '/');
  const char *basename = path_copy;
  char *parent = ".";
  if (slash) {
    *slash = '\0';
    parent = path_copy;
    basename = slash + 1;
  }
  if (!basename[0]) {
    errno = EINVAL;
    return fail("empty basename");
  }

  int root_fd = open(root, O_RDONLY | O_DIRECTORY | O_CLOEXEC | O_NOFOLLOW);
  if (root_fd < 0) return fail("open worktree root");
  struct stat root_status;
  if (fstat(root_fd, &root_status) < 0 || !S_ISDIR(root_status.st_mode) || root_status.st_uid != getuid()) {
    errno = EPERM;
    return fail("unsafe worktree root");
  }
  int parent_fd = open_parent_beneath(root_fd, parent);
  if (parent_fd < 0) return fail("openat2 parent beneath root");
  struct stat parent_status;
  if (fstat(parent_fd, &parent_status) < 0 || !S_ISDIR(parent_status.st_mode) || parent_status.st_uid != getuid()) {
    errno = EPERM;
    return fail("unsafe destination parent");
  }

  struct stat existing_status;
  int exists = fstatat(parent_fd, basename, &existing_status, AT_SYMLINK_NOFOLLOW) == 0;
  char before_hash[65] = {0};
  if (exists) {
    if (!verify_regular_stat(&existing_status)) {
      errno = EPERM;
      return fail("unsafe existing destination");
    }
    int existing_fd = openat(parent_fd, basename, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (existing_fd < 0 || sha256_fd(existing_fd, before_hash) < 0) return fail("hash existing destination");
    close(existing_fd);
    if (base_length != 64 || strcmp(before_hash, expected_base) != 0) {
      errno = ESTALE;
      return fail("base digest mismatch");
    }
  } else {
    if (errno != ENOENT) return fail("inspect destination");
    if (base_length != 1 || expected_base[0] != '-') {
      errno = ESTALE;
      return fail("destination unexpectedly absent");
    }
  }

  char temp_name[128];
  struct timespec now;
  clock_gettime(CLOCK_MONOTONIC, &now);
  snprintf(temp_name, sizeof(temp_name), ".design-writer-%ld-%ld-%ld.tmp", (long)getpid(), (long)now.tv_sec, now.tv_nsec);
  int temp_fd = openat(parent_fd, temp_name, O_CREAT | O_EXCL | O_RDWR | O_CLOEXEC | O_NOFOLLOW, 0600);
  if (temp_fd < 0) return fail("create temporary destination");
  size_t written = 0;
  while (written < content_length) {
    ssize_t count = write(temp_fd, content + written, (size_t)(content_length - written));
    if (count < 0) {
      if (errno == EINTR) continue;
      unlinkat(parent_fd, temp_name, 0);
      return fail("write temporary destination");
    }
    written += (size_t)count;
  }
#ifdef DESIGN_TEST_FAIL_TEMP_FSYNC
  errno = EIO;
  int temp_fsync_result = -1;
#else
  int temp_fsync_result = fsync(temp_fd);
#endif
  if (temp_fsync_result < 0) {
    unlinkat(parent_fd, temp_name, 0);
    return fail("fsync temporary destination");
  }
  struct stat temp_status;
  if (fstat(temp_fd, &temp_status) < 0 || !verify_regular_stat(&temp_status)) {
    unlinkat(parent_fd, temp_name, 0);
    errno = EPERM;
    return fail("unsafe temporary destination");
  }
  char after_hash[65];
  if (sha256_fd(temp_fd, after_hash) < 0) {
    unlinkat(parent_fd, temp_name, 0);
    return fail("hash temporary destination");
  }
  close(temp_fd);

  struct stat revalidated;
  int still_exists = fstatat(parent_fd, basename, &revalidated, AT_SYMLINK_NOFOLLOW) == 0;
  if (still_exists != exists || (exists && (revalidated.st_ino != existing_status.st_ino || revalidated.st_dev != existing_status.st_dev))) {
    unlinkat(parent_fd, temp_name, 0);
    errno = ESTALE;
    return fail("destination changed during write");
  }
  if (exists) {
    int revalidated_fd = openat(parent_fd, basename, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    char revalidated_hash[65];
    if (revalidated_fd < 0 || sha256_fd(revalidated_fd, revalidated_hash) < 0 || strcmp(revalidated_hash, before_hash) != 0) {
      if (revalidated_fd >= 0) close(revalidated_fd);
      unlinkat(parent_fd, temp_name, 0);
      errno = ESTALE;
      return fail("destination bytes changed during write");
    }
    close(revalidated_fd);
  }
#ifdef DESIGN_TEST_FAIL_RENAME
  errno = EIO;
  int rename_result = -1;
#else
  int rename_result = (int)syscall(SYS_renameat2, parent_fd, temp_name, parent_fd, basename, 0);
  if (rename_result < 0 && errno == ENOSYS) rename_result = renameat(parent_fd, temp_name, parent_fd, basename);
#endif
  if (rename_result < 0) {
    unlinkat(parent_fd, temp_name, 0);
    return fail("atomic rename destination");
  }
#ifdef DESIGN_TEST_FAIL_DIRECTORY_FSYNC
  errno = EIO;
  int directory_fsync_result = -1;
#else
  int directory_fsync_result = fsync(parent_fd);
#endif
  if (directory_fsync_result < 0) return fail("fsync destination directory");

  if (exists) {
    printf("{\"before_sha256\":\"%s\",\"after_sha256\":\"%s\",\"bytes\":%llu,\"pid\":%ld,\"ppid\":%ld,\"build_id\":\"%s\",\"protocol_version\":\"%s\"}\n",
           before_hash, after_hash, (unsigned long long)content_length, (long)getpid(), (long)getppid(), DESIGN_BUILD_ID, DESIGN_PROTOCOL_VERSION);
  } else {
    printf("{\"before_sha256\":null,\"after_sha256\":\"%s\",\"bytes\":%llu,\"pid\":%ld,\"ppid\":%ld,\"build_id\":\"%s\",\"protocol_version\":\"%s\"}\n",
           after_hash, (unsigned long long)content_length, (long)getpid(), (long)getppid(), DESIGN_BUILD_ID, DESIGN_PROTOCOL_VERSION);
  }
  close(parent_fd);
  close(root_fd);
  free(root);
  free(relative);
  free(expected_base);
  free(content);
  free(path_copy);
  return 0;
}
