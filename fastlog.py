from fastlog import log
import traceback

log.info("Familiar log functions:")
log.info("log.info")
log.success("log.success")
log.failure("log.failure")
log.debug("You don't see me! The default level is log.INFO")
log.setLevel(log.DEBUG)
log.debug("log.debug")
log.warning("log.warning")
try:
    log.exception("log.exception")
except Exception as e:
    traceback.print_exc()
    pass

log.separator()

log.info("Indent logs using Python's 'with:'")

log.warning("First level block")
with log.indent():
    log.warning("Second level block")
    with log.indent():
        log.warning("Third level block")
    log.warning("Back to second")
log.warning("Back to first")

log.separator()

from fastlog import hexdump

log.hexdump(list(map(chr, range(256))))