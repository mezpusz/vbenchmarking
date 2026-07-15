#!/bin/bash

set -euo pipefail

tail -n +7 $1 | /home/mhajdu/GDV/GDV -u -d
