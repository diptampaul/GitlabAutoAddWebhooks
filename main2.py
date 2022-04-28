import gitlab, requests, json
from tabulate import tabulate
from datetime import date

#Get the access using private token
def get_access(private_token):
    url = "https://gitlab.com"
    try:
        gl = gitlab.Gitlab(url = url, private_token=private_token)
    except:
        print("Error Occured")
    return gl
    

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

#List the projects name with id in tabular form
def list_of_projects(gl):
    try:
        projects = gl.projects.list(owned=True)
        details = []
        for project in projects:
            details.append([project.id, project.name])
        print("\n\n\n") 
        print(tabulate(details, headers=['Project ID', 'Project Name']))
        print("\n\n\n") 
        
    except Exception as e:
        print(e)


def test_hook():
    pass

#Send notification to teams regarding the webhook addition
def bool_conversion(int_value):
    if int_value == 1:
        return True
    else:
        return False
    
def notify_team(data, project_id, project_name):
    facts = []
    webhook_url = "https://addverbtech.webhook.office.com/webhookb2/66d0b5ea-66ca-4131-8e91-f94d3ae3e895@9d0bf1ed-9dbb-4ad2-b95e-efaf17869937/IncomingWebhook/618fe7c20e844aa9be73b81cbecaf97e/20ff3628-3d49-4d11-89ca-63e7e7852be2"
    
    #adding webhook url and secret token
    facts.append({"name": "Webhook URL", "value": data["url"]})
    if data["token"] == '':
        facts.append({"name": "secret Token", "value": "NULL"})
    else:
        facts.append({"name": "secret Token", "value": data["token"]})
    facts.append({"name": "SSL Activation", "value": bool_conversion(data["enable_ssl_verification"])})
    #adding rest of the values
    true_values = []
    for k,v in data.items():
        if v == 1 and k != "enable_ssl_verification":
            true_values.append(k)
    facts.append({"name": "Trigger Values", "value": " , ".join(true_values)})
    #print(facts)
    data = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "themeColor": "0076D7",
        "summary": "New Gitlab Webhook Added",
        "sections": [{
            "activityTitle": f"Project Name {project_name}",
            "activitySubtitle": f"New Gitlab Webhook Added - {str(date.today())}",
            "activityImage": "https://teamsnodesample.azurewebsites.net/static/img/image5.png",
            "facts": facts,
            "text": f"Project ID : {project_id}"
        }],
    }
    r = requests.post(webhook_url, data= json.dumps(data), headers={'Content-Type': 'application/json'})

#Get all the project id owned by the user
def get_project_ids(gl):
    try:
        ids = []
        projects = gl.projects.list(owned=True)
        for project in projects:
            ids.append(project.id)
        return ids
        
    except Exception as e:
        print(e)
  
#Adding the webhook      
def add_webhooks(data, gl, project_id):
    project = gl.projects.get(project_id)
    #hooks = project.hooks.list()
    try:
        hook = project.hooks.create(data)
        print(f'Added Webhook Details : {hook}\n\n')
    except Exception as e:
        print(e)
    test_hook()
    notify_team(data, project_id, project.name)
    
#Get id of all the webhooks of a particular project
def list_of_webhooks(gl,project_id):
    project = gl.projects.get(project_id)
    hooks = project.hooks.list()
    hook_details = []
    for hook in hooks:
        #print(hook)
        hook_details.append([hook.id, hook.url])
    
    print("\n\n\n")
    print(f"  For Project {project.name} (ID : {project_id})")
    if len(hook_details) == 0:
        print("There are no webhooks for this project ")
    else:
        print(tabulate(hook_details, headers=['Hook ID', 'Hook URL']))  
    print("\n\n\n")  
    return hook_details
    
#Deleting the webhooks
def delete_webhook(gl, project_id, webhook_id):
    project = gl.projects.get(project_id)
    try:
        hook = project.hooks.delete(webhook_id)
        print(f'Deleting {webhook_id}')
    except Exception as e:
        print(e)


if __name__ == "__main__":
    
    #Taking arguments
    filename = 'PRIVATE_KEY.txt'

    #Get credentials
    creds = get_credentials(filename)
    #print(creds)
    
    #SetUp Access
    gl = get_access(creds["PERSONAL_ACCESS_TOKEN"])
    
    while True:
        loop_decision = input("-- Write 'ADD' or 'A' to add a webhook\n-- Write 'DELETE' or 'D' to delete webhooks\n-- Press Enter to QUIT\nYour Choice :: ")
        
        
        if loop_decision.upper() == 'ADD' or loop_decision.upper() == 'A':
            project_ids = []
            #Get the project ids and names
            decision = input("Do you want to add web hook in all the projects? Y OR N | Default Y : ")
            if decision == 'N' or decision == 'n':
                #print (here is the list of projects ) --> listofProjects()
                list_of_projects(gl)
                x = input("Enter the project IDs (separated by space): ")
                for id in x.split(' '):
                    project_ids.append(id)

            elif decision == 'Y' or decision == '' or  decision == ' ' or decision == 'y':
                project_ids = get_project_ids(gl)   
            else:
                continue
                
            #Setting up the data
            data = {
                "url": creds["WEBHOOK_URL"],
                #Set the belows to True as per need
                "confidential_issues_events": [1 if eval(creds["confidential_issues_events"]) == True else 0][0], 
                "confidential_note_events": [1 if eval(creds["confidential_note_events"]) == True else 0][0],
                "deployment_events":[1 if eval(creds["deployment_events"]) == True else 0][0],
                "issues_events":[1 if eval(creds["issues_events"]) == True else 0][0],
                "job_events":[1 if eval(creds["job_events"]) == True else 0][0],
                "merge_requests_events":[1 if eval(creds["merge_requests_events"]) == True else 0][0],
                "note_events":[1 if eval(creds["note_events"]) == True else 0][0],
                "pipeline_events":[1 if eval(creds["pipeline_events"]) == True else 0][0],
                "releases_events":[1 if eval(creds["releases_events"]) == True else 0][0],
                "wiki_page_events":[1 if eval(creds["wiki_page_events"]) == True else 0][0],
                "tag_push_events":[1 if eval(creds["tag_push_events"]) == True else 0][0],
                "push_events":[1 if eval(creds["push_events"]) == True else 0][0],
                "enable_ssl_verification":[1 if eval(creds["enable_ssl_verification"]) == True else 0][0],
                #Add Secret token to validate received payloads; this isn’t returned in the response.
                "token": creds["token"]
            }
            
            #Adding the webhook
            for id in project_ids:
                try:
                    add_webhooks(data=data, gl=gl, project_id=id)
                except:
                    continue
                
                
                
        elif loop_decision.upper() == 'DELETE' or loop_decision.upper() == 'D':
            project_ids = []
            #Get the project ids and names
            decision = input("Do you want to remove web hook from all the projects? Y OR N | Default Y : ")
            if decision == 'N' or decision == 'n':
                #print (here is the list of projects ) --> listofProjects()
                list_of_projects(gl)
                x = input("Enter the project IDs (separated by space): ")
                for id in x.split(' '):
                    project_ids.append(id)

            elif decision == 'Y' or decision == '' or  decision == ' ' or decision == 'y':
                project_ids = get_project_ids(gl)   
            else:
                continue

            #Deleting webhooks
            for p_id in project_ids:
                hook_details = list_of_webhooks(gl, p_id)
                if len(hook_details) == 0:
                    continue
                
                #Getting the hook ids
                webhook_ids = []
                webhook_decision = input("Delete all Webhooks ?  Y OR N | Default Y : ")
                if webhook_decision == 'N' or webhook_decision == 'n':
                    w_ids = input("Enter the webhook ids separated by space : ")
                    for w_id in w_ids.split(' '):
                        webhook_ids.append(w_id)
                elif webhook_decision == 'Y' or webhook_decision == '' or webhook_decision == ' ' or webhook_decision == 'y':
                    for hook_detail in hook_details:
                        webhook_ids.append(hook_detail[0])
                else:
                    print("Invalid Input")
                    break

                #Deleting webhook
                for w_id in webhook_ids:
                    delete_webhook(gl,project_id=p_id, webhook_id=w_id)
                
        
        
        else:
            print('\nQuiting ... ')
            break
        