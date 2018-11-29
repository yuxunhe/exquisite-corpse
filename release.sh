#!/bin/bash

pipenv lock -r requirements.txt
flask init-db
