from fastlog import log
log.setLevel(log.DEBUG)

log.info("log.info")
log.success("log.success")
log.failure("log.failure")

with log.indent():
    log.debug("log.debug")
    log.warning("log.warning")

log.separator()

log.hexdump(list(map(chr, range(256))))