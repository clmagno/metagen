#generator.py

import json
import csv
import sys

def load_config(config_filename):
    try:
        with open(config_filename, 'r') as json_file:
            config = json.load(json_file)
        return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

def generate_csv(config):
    
    filename_template = config["filename_template"]
    jira_id = config["jira_id"]
    
    
    
    if "COL" in filename_template :
        columns = config["columns"]
        temp_db_names = config["tgt_db_names"]
        environments = config["environments"]
        tgt_db_names = []
        for env in environments:
            for db in temp_db_names:
                tgt_db_names.append(f"{env}_{db}")
        csv_rows = []
        for table_name, table_config in config.items():
            
            if table_name not in ["filename_template", "columns", "jira_id", "tgt_db_names","environments","trans_col_file"]:

                for tgt_db_name in tgt_db_names:
                    
                    for row_num, row_data in table_config.items():
                        tgt_table_name = table_name
                        csv_rows.append([jira_id, tgt_db_name, tgt_table_name, row_num] + row_data)
        output_filename = filename_template.replace("{{ JIRA_ID }}", jira_id.replace("-", "_"))
        with open(output_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(columns)
            csv_writer.writerows(csv_rows)

        print(f"CSV file '{output_filename}' created successfully.")
    elif "TABLE" in filename_template:
        hdfs_folder = config["hdfs_folder"]
        columns = config["columns"]
        temp_db_names = config["tgt_db_names"]
        environments = config["environments"]
        tgt_db_names = []
        
        for env in environments:
            for db in temp_db_names:
                tgt_db_names.append(f"{env}_{db}")
        
        values = []
        
        for table_name, table_config in config.items():
            if table_name not in ["jira_id","hdfs_folder","filename_template","columns","environments","tgt_db_names"]:
                tgt_hdfs_locs = []
                for env  in  environments:
                    tgt_hdfs_loc = config[table_name][1].replace("{{ environment }}",env).replace("{{ hdfs_folder }}",hdfs_folder).replace("{{ TGT_TABLE_NAME }}",table_name)
                    tgt_hdfs_locs.append(tgt_hdfs_loc)
                config[table_name][1]=tgt_hdfs_loc
                for tgt_db in tgt_db_names:
                    if tgt_db.split("_")[-1] in tgt_hdfs_loc:
                        tgt_format = config[table_name]
                        values.append([jira_id,tgt_db,table_name]+config[table_name])
        output_filename = filename_template.replace("{{ JIRA_ID }}", jira_id.replace("-", "_"))
        with open(output_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(columns)
            csv_writer.writerows(values)

        print(f"CSV file '{output_filename}' created successfully.")   
    elif "VIEW" in filename_template:
        columns = config["columns"]
        environments = config["environments"]
        values = []
        for table_name, table_config in config.items():
            if table_name not in ["jira_id","filename_template","columns","environments"]:
                src_db_name = config[table_name]["src_db_name"]
                src_table_name = config[table_name]["src_table_name"]
                temp_db_name = config[table_name]["tgt_db_name"]

                tgt_view_name = table_name
                status = config[table_name]["status"]

                
                for env in environments:
                    
                    config[table_name]["tgt_db_name"] = f"{env}_{temp_db_name}"
                    tgt_db_name = config[table_name]["tgt_db_name"]
                    values.append([jira_id, src_db_name,src_table_name,tgt_db_name,tgt_view_name,status])
        output_filename = filename_template.replace("{{ JIRA_ID }}", jira_id.replace("-", "_"))
        with open(output_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(columns)
            csv_writer.writerows(values) 
        print(f"CSV file '{output_filename}' created successfully.")   
        
                
def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py metadata_config.json")
        sys.exit(1)

    config_filename = sys.argv[1]
    config = load_config(config_filename)
    for i in config:
        generate_csv(config[i])

if __name__ == "__main__":
    main()

