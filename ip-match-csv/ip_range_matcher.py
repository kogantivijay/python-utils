import csv
import ipaddress
import os

def is_header(row):
    """Check if the row consists of non-numeric values (indicative of a header)."""
    return all(not item.replace('.', '', 1).isdigit() for item in row)

def read_csv(file_path, delimiter=','):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        first_row = next(reader, None)  # Read the first row
        if first_row is None:
            return []  # Empty file

        if is_header(first_row):
            data = list(reader)  # Read the rest if the first row is header
        else:
            data = [first_row] + list(reader)  # Include the first row if it's not header

        return data


def is_ip_in_range_or_cidr(ip, range_or_cidr):
    if '-' in range_or_cidr:
        start_ip, end_ip = range_or_cidr.split('-')
        start_ip = ipaddress.ip_address(start_ip.strip())
        end_ip = ipaddress.ip_address(end_ip.strip())
        ip = ipaddress.ip_address(ip)
        return start_ip <= ip <= end_ip
    else:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(range_or_cidr, strict=False)

def process_ips(ip_file, cidr_file):
    ips = read_csv(ip_file)
    cidr_data = read_csv(cidr_file, delimiter='|')
    account_matches = {}
    ip_match_details = {}

    for ip in ips:
        matched_accounts = []
        for account, cidr_list in cidr_data:
            cidrs = cidr_list.strip("[]").split(",")
            for cidr in cidrs:
                if is_ip_in_range_or_cidr(ip[0], cidr.strip().strip("'").strip('"')):
                    matched_accounts.append(account)
                    account_matches[account] = account_matches.get(account, 0) + 1
                    break

        if matched_accounts:
            ip_match_details[ip[0]] = matched_accounts
        else:
            ip_match_details[ip[0]] = None

    return account_matches, ip_match_details

def write_results(account_matches, ip_match_details):
    with open('ip-match-csv/result_ips_matched.csv', 'w', newline='') as file_matched, \
         open('ip-match-csv/result_ips_not_matched.csv', 'w', newline='') as file_not_matched, \
         open('ip-match-csv/result_account_summary.csv', 'w', newline='') as file_summary:

        writer_matched = csv.writer(file_matched, delimiter='|')
        writer_not_matched = csv.writer(file_not_matched, delimiter='|')
        writer_summary = csv.writer(file_summary, delimiter='|')

        writer_matched.writerow(['IP', 'AccountNumbers'])
        writer_not_matched.writerow(['IP'])
        writer_summary.writerow(['Account', 'Matches'])

        for ip, accounts in ip_match_details.items():
            if accounts:
                writer_matched.writerow([ip, ','.join(accounts)])
            else:
                writer_not_matched.writerow([ip])

        for account, count in account_matches.items():
            writer_summary.writerow([account, count])


# Example usage
print("Current working directory:", os.getcwd())
account_matches, ip_match_details = process_ips('ip-match-csv/ips.csv', 'ip-match-csv/account_cidrs.csv')
write_results(account_matches, ip_match_details)



