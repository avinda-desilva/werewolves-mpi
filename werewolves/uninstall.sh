#!/bin/bash

userdel moderator
groupdel moderator
for i in {0..15}; do userdel player$i; done
for i in {0..15}; do groupdel player$i; done
