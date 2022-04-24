import requests, json, argparse

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


#Getting the personal access token, webhook and other additional datas from text file
def get_credentials(filename):
    d = {}
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
        for line in lines:
            if line[0] != "#":
                line = line.split(":",1)
                d[line[0]] = line[-1]
    return d

#Get all the project ids
def get_project_ids(privateToken):
    url = 'https://gitlab.com/api/v4/projects?owned=true'
    #response = requests.get(url, headers={"PRIVATE-TOKEN": privateToken})
    response = requests.get(url, auth=BearerAuth(privateToken))
    response_dict = json.loads(response.text)
    #print(response_dict)
    d = []
    for i in range(len(response_dict)):
        id = response_dict[i]['id']
        name = response_dict[i]['name']
        d.append({"project_id": id, "project_name": name})
    return d


#Add the webhooks to every urls
def add_webhook(private_token, project_id, data):
    url = f'https://gitlab.com/api/v4/projects/{project_id}/hooks'
    try:
        #r = requests.post(url, data = json.dumps(data), headers={"PRIVATE-TOKEN": private_token, "Content-Type": "application/json"})
        r = requests.post(url, data = json.dumps(data), auth=BearerAuth(private_token), headers={"Content-Type": "application/json"})
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
    except requests.exceptions.RequestException as err:
        print ("OOps: Something Else",err)




if __name__ == '__main__':
    #Taking arguments
    filename = 'PRIVATE_KEY.txt'

    #Get credentials
    creds = get_credentials(filename)
    #print(creds)

    project_details = []
    #Get the project ids and names
    decision = input("Do you want to fetch all the ids? Y OR N | Default Y : ")
    if decision == 'N':
        project_details = []
        x = input("Enter the project IDs (separated by space): ")
        for id in x.split(' '):
            project_details.append({"project_id": id})

    elif decision == 'Y' or decision == '' or  decision == ' ':
        project_details = get_project_ids(creds["PERSONAL_ACCESS_TOKEN"])   
    else:
        print("Invalid Input")
        
    #for every project id, add the webhook with arguments
    if len(project_details) != 0:
        #Add the webhooks
        for project_detail in project_details:
            data = {
                "url": creds["WEBHOOK_URL"],
                #Set the belows to True as per need
                "confidential_issues_events": eval(creds["confidential_issues_events"]), 
                "confidential_note_events": eval(creds["confidential_note_events"]),
                "deployment_events":eval(creds["deployment_events"]),
                "issues_events":eval(creds["issues_events"]),
                "job_events":eval(creds["job_events"]),
                "merge_requests_events":eval(creds["merge_requests_events"]),
                "note_events":eval(creds["note_events"]),
                "pipeline_events":eval(creds["pipeline_events"]),
                "releases_events":eval(creds["releases_events"]),
                "wiki_page_events":eval(creds["wiki_page_events"]),
                "tag_push_events":eval(creds["tag_push_events"]),
                "push_events":eval(creds["push_events"]),
                "enable_ssl_verification":eval(creds["enable_ssl_verification"]),
                #Add Secret token to validate received payloads; this isn’t returned in the response.
                "token": creds["token"]
            }
            #print(data)
            add_webhook(private_token=creds["PERSONAL_ACCESS_TOKEN"], data=data, project_id=project_detail["project_id"])
    else:
        print("Re-run the code")
