#!/bin/bash
conda env export --from-history | grep -v "^prefix: " > uzhikEnvironment.yml