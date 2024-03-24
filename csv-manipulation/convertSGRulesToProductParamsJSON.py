import csv
import json
import os
import argparse

def group_data_by_groupname(filepath, env_filters):
    data = {}
    env_filters = [env.lower() for env in env_filters]

    with open(filepath, mode='r', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter='|')

        for row in reader:
            if row['Env'].lower() in env_filters:
                group = row['GroupName']
                if group not in data:
                    data[group] = []
                data[group].append(row)
    
    return data

def format_grouped_data_to_json(grouped_data):
    output = []
    rule_number = 1

    for group, rows in grouped_data.items():
        for row in rows:
            # Check both 'cidr-range' and 'sg-reference' and format accordingly
            cidr_range = row.get('cidr-range', '')
            sg_reference = row.get('sg-reference', '')
            cidr_or_sgref = f"{cidr_range},{sg_reference}"

            formatted_value = ",".join([row['GroupName'], row['Type'], row['Protocol'], row['fromPort'], row['toPort'], cidr_or_sgref, row['Description']])
            output.append({"key": f"Rule{rule_number}", "Value": formatted_value})
            rule_number += 1

    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Group CSV data by GroupName and convert to JSON with incremental rule numbers.')
    parser.add_argument('--csv_file_path', type=str, required=True, help='The file path to the CSV file.')
    parser.add_argument('--env_include', type=str, required=True, help='Comma-separated list of environments to include in the filter.')
    parser.add_argument('--output_path', type=str, required=True, help='The file path for the output JSON file.')
    
    args = parser.parse_args()

    # Split the env_include argument on commas to handle comma-separated values
    env_filters = args.env_include.split(',')

    grouped_data = group_data_by_groupname(args.csv_file_path, env_filters)
    json_output = format_grouped_data_to_json(grouped_data)

    # Write the output to a file
    with open(args.output_path, 'w') as output_file:
        output_file.write(json_output)

    print(f"Output written to {args.output_path}")

if __name__ == "__main__":
    main()
