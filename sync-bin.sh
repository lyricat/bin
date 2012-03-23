#!/bin/bash
rsync --progress --existing -azvh ${THIRD_BIN_PATH} ${MYBIN}
rsync --progress --update -azvh ${MYBIN_DEV} ${MYBIN}
echo "Done."
