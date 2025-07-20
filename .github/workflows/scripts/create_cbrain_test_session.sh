
#
# This script just echoes back the
# content of the credentials.json file
# needed by the 'cbrain' command line program;
# the token in there is the same as used
# in the CBRAIN api test framework, only
# valid within the test database set up there.
#
# Once we have support for multiple distinct
# sessions in parallel with the cbrain client,
# we'll create records for the other tokens too.
#

# The tree tokens used by the test suite;
# for the moment we only use the NORM one
ADMIN_TOKEN="0123456789abcdef0123456789abcdef";
NORMAL_TOKEN="0123456789abcdeffedcba9876543210";
DEL_TOKEN="0123456789abcdefffffffffffffffff";

# Timestamp as expected by the cbrain client program
timestamp=$(date +"%Y-%m-%dT%H:%M:%S")
cat <<CREDJSON
{
  "cbrain_url": "http://localhost:3000",
  "api_token":  "$NORMAL_TOKEN",
  "user_id":    2,
  "timestamp":  "$timestamp"
}
CREDJSON
