## Python - Cloudformation template - AWS VPC setup Demo

This Repository Contains Python script to create aws cloudformation template by using troposphere Library and deploy the CF template in multiple AWS account.

CF is responsible for creating -

- VPC basic setup
- Private subnets (No internet access)
- Public subnets (Outbound internet access)
- Protected subnets (Outbound internet access via NAT)
- NAT for Protected subnets
____________________________________________________________________________________________________________

To deploy to AWS using Github Actions:
Add the secret key and access key as Environment secrets in Github repo for Administrator Account

AWS_ACCESS_KEY_ID 

AWS_SECRET_ACCESS_KEY

____________________________________________________________________________________________________________

Before you create a stack set with self-managed permissions, you need to establish a trust relationship between the administrator and target accounts by creating IAM roles in each account.
Please check this link to setup roles.
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/stacksets-prereqs-self-managed.html

![image](https://user-images.githubusercontent.com/118276846/202184108-7e26a8bf-c04c-4a26-8afc-6d1f56ccf0e0.png)


____________________________________________________________________________________________________________

Running a workflow  

1- On GitHub.com, navigate to the main page of the repository.

2- Under your repository name, click Actions.  

3- In the left sidebar, click the workflow you want to run. 

4- Above the list of workflow runs, select Run workflow.

5- Use the Branch dropdown to select the workflow's branch, and select the input parameters. 

6- Enter the Target AWS Account id.

7- Select the region 

8- Click Run workflow.
____________________________________________________________________________________________________________


____________________________________________________________________________________________________________

Steps in deployment

1- Workflow will install the dependencies.

2- Using python3 it will run the python code and generate the cloudformation JSON template.

3- Validate the CF template

3- Create a stackset in administrator aws account.

4- Deploy the stacks to target accounts.
____________________________________________________________________________________________________________
