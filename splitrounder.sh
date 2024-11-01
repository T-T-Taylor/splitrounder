#!/bin/bash

python_files=(
	"rss-new.py"
	"2.confirmation-loop.py"
	"2.contact-list.py"
	"2.otp-generation.py"
        "2.otp-request.py"
)

#Kill Function

for python_file in "${python_files[@]}"; do
	pkill -f "python3 $script_path"
done

#Run the Python Files

for python_file in "${python_files[@]}"; do
	python3 "$python_file" &
done
