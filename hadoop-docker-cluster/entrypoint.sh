#!/bin/bash

# Start SSH service
service ssh start

# Execute the command passed to docker run
exec "$@"