import csv
import json
import ipaddress

def cidr_to_es_range(cidr):
    """Convert a CIDR to Elasticsearch range query format."""
    network = ipaddress.ip_network(cidr, strict=False)  # Use strict=False to avoid the ValueError
    return {
        "range": {
            "client.ip": {
                "gte": str(network[0]),
                "lte": str(network[-1])
            }
        }
    }

def process_csv(file_name):
    query_clauses = []
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        for row in reader:            
            if 'CIDRS' in row and row['CIDRS']:  # Check if cidrs is not None and not an empty string
                cidrs = row['CIDRS']
                try:
                    # Load CIDRs as JSON if it's a list, otherwise treat as a single string
                    cidr_list = json.loads(cidrs) if cidrs.startswith('[') else [cidrs]
                except json.JSONDecodeError:
                    cidr_list = [cidrs]

                for cidr in cidr_list:
                    range_query = cidr_to_es_range(cidr)
                    query_clauses.append(range_query)

    return query_clauses

csv_file = 'ip-match-csv/account_cidrs.csv'
ranges = process_csv(csv_file)
print(json.dumps(ranges, indent=4))

