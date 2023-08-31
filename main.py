import streamlit as st
from langchain import PromptTemplate
from langchain.callbacks import get_openai_callback
from streamlit_modal import Modal
import streamlit.components.v1 as components
import os
import openai
from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage
from tabulate import tabulate


def main():
    st.set_page_config(page_title="Budget Pro", page_icon=":pdf:", layout="wide")
    st.header("Budget Planner 💸 ")

    # # Configure OpenAI API
    openai.api_type = st.secrets["OPENAI_API_TYPE"]
    openai.api_version = st.secrets["OPENAI_DEPLOYMENT_VERSION"]
    openai.api_base = st.secrets['OPENAI_DEPLOYMENT_ENDPOINT']
    openai.api_key = st.secrets["OPENAI_API_KEY"]

    if 'vms' not in st.session_state:
        st.session_state.vms = []

    if 'disks' not in st.session_state:
        st.session_state.disks = []

    if 'backup' not in st.session_state:
        st.session_state.backup = []

    if 'paasDB' not in st.session_state:
        st.session_state.paasDB = []

    col1, col2 = st.columns(2)

    with col1:
        modal_vm = Modal(key="vm", title="VM")
        open_modal = st.button("Add Vm")
        if open_modal:
            modal_vm.open()
        st.dataframe(st.session_state.vms)

        # modal_backup = Modal(key="backup", title="Backup")
        # open_modal_backup = st.button("Add Backup")
        # if open_modal_backup:
        #     modal_backup.open()
        # st.dataframe(st.session_state.backup)

    with col2:
        modal_disk = Modal(key="disk", title="Disk")
        open_modal_disk = st.button("Add Disk")
        if open_modal_disk:
            modal_disk.open()
        st.dataframe(st.session_state.disks)

        # modal_paasDB = Modal(key="paasDB", title="PaaS DB")
        # open_modal_paasDB = st.button("Add PaaS DB")
        # if open_modal_paasDB:
        #     modal_paasDB.open()
        # st.dataframe(st.session_state.paasDB)

    if modal_vm.is_open():
        with modal_vm.container():
            st.write("Add VM")

            with st.form('Add new VM'):
                env = st.selectbox('Environment', ['DEV', 'PRF', 'PROD'])
                VM_Name = st.text_input("VM Name")
                Cpu_Cores = st.number_input("CPU Cores", min_value=1)
                Ram = st.number_input("RAM (GB)", min_value=0)
                Hour_Month = st.number_input("Hours/Month", min_value=1)
                submit = st.form_submit_button("Add VM")
                if submit:
                    st.session_state.vms.append(
                        {"env": env, "VM_Name": VM_Name, "Cpu_Cores": Cpu_Cores, "Ram": Ram, "Hour_Month": Hour_Month})

    if modal_disk.is_open():
        with modal_disk.container():
            st.write("Add Disk")
            with st.form('Add new Disk'):
                env_disk = st.selectbox('Environment', ['DEV', 'PRF', 'PROD'])
                VM_attached = st.selectbox("VM Attached", [vm["VM_Name"] for vm in st.session_state.vms])
                Disk_Size = st.number_input("Disk Size", min_value=1)
                Disk_type = st.text_input("Disk Type")
                submit_disk = st.form_submit_button("Submit")
                if submit_disk:
                    st.session_state.disks.append(
                        {"env_disk": env_disk, "VM_attached": VM_attached, "Disk_Size": Disk_Size,
                         "Disk_type": Disk_type})

    # if modal_backup.is_open():
    #     with modal_backup.container():
    #         st.write("Add Backup")
    #         with st.form('Add new Backup'):
    #             VM_to_backup = st.selectbox("VM To backup", [vm["VM_Name"] for vm in st.session_state.vms])
    #             Backup_Size = st.number_input("Backup Size", min_value=1)
    #             Backup_type = st.text_input("Backup Type")
    #             submit_backup = st.form_submit_button("Submit")
    #             if submit_backup:
    #                 st.session_state.backup.append(
    #                     {"VM_to_backup": VM_to_backup, "Backup_Size": Backup_Size,
    #                      "Backup_type": Backup_type})
    #
    # if modal_paasDB.is_open():
    #     with modal_paasDB.container():
    #         st.write("Add PaaS DB")
    #         with st.form('Add new PaaS DB'):
    #             env_paasDB = st.selectbox('Environment', ['DEV', 'PRF', 'PROD'])
    #             DB_Name = st.text_input("DB Name")
    #             DB_type = st.selectbox("DB Type", [
    #                 "Azure Database for PostgreSQL flexible servers",
    #                 "Azure Database for PostgreSQL servers", "Azure Database for MySQL servers"
    #                 , "Azure SQL Database", "Azure SQL Managed Instance ", "Azure Database for MySQL flexible servers"])
    #             DB_Size = st.number_input("DB Size", min_value=1)
    #             submit_paasDB = st.form_submit_button("Submit")
    #             if submit_paasDB:
    #                 st.session_state.paasDB.append(
    #                     {"env_paasDB": env_paasDB, "DB_Name": DB_Name, "DB_Size": DB_Size,
    #                      "DB_type": DB_type})

    txt = st.text_area(height=10, label='Add other type of resource')

    template = ''' As a FinOps Practitioner at Carrefour, your role is to manage the financial operations related to cloud usage.
            Currently, various teams within Carrefour are developing a cloud-based application and seek your expertise to create a budget for it.
            For this project, the chosen cloud provider is {cloud_provider}. 
            They have provided detailed information about the app's required resources, which include Virtual Machines and persistent disks.
            Your task is to create a comprehensive budget for the application using the public pricing of {cloud_provider}.

            Here's an illustrative example of done by a FinOps practitioner at Carrefour for a similar project hosted on Azure:

            In this example, the VMs are:

            | Environment | VM Name                  | CPU Cores | RAM (GB) | Hours/Month |
            |-------------|--------------------------|-----------|----------|-------------|
            | PRF         | Reporting SSRS           | 16        | 64       | 300         |
            | PRD         | Database SSRS            | 16        | 64       | 730         |
            | PRD         | Reporting                | 32        | 64       | 730         |

            For the persistent disk:

            | Environment | VM Name             | Disk Size (GB) | Disk Type    |
            |-------------|---------------------|----------------|--------------|
            | REC         | Base de données     | 4000           | Standard_HDD |
            | PRF         | Transactionnelle    | 4000           | Premium_SSD  |
            | PRD         | Transactionnelle2   | 4000           | Premium_SSD  |

            From the above information, the FinOps practitioner created the following budget:

            He generated two tables: one for Virtual Machines and one for Disks.
            The Virtual Machine table has the following columns:
            | ENV | VM              | CPU | RAM | Hours/Month | VM Gabarit | VMHourlyCost | Cost   | BackupCost |

            The VM Gabarit is a suggestion from the Azure's VM templates, considering CPU and RAM.
            VMHourlyCost is the hourly cost of the VM Gabarit in Azure's public pricing in Euro.
            Cost is the monthly cost of the VM, calculated as Hours/Month * VMHourlyCost.
            BackupCost is the cost of backup for this specific VM Gabarit.

           As result, the VM table looks like this:
           ENV	        VM	                        CPU	    RAM	    Hours/Mo	Gabarit	    VMHourlyCost	VM Cost	    Backup Cost
           PRF Serveur de reporting SSRS	        16	    64	     300	    D16s_v3	      €0.73 	    €219	    €0
           PRD	Serveur de reporting SSRS	        16	    64	     730	    D16s_v3	      €0.73	        €533	    €37
           REC	Base de données transactionnelle	8	    32	     300	    D8s_v3	      €0.37	        €111	    €290
           PRF	Base de données transactionnelle	32	    875	     300	    M32ms	      €6.80	        €2,040	    €0
           PRD	Base de données transactionnelle	32	    875	     730	    M32ms	      €6.80	        €4,964	    €343
           REC	Base de données reporting	        8	    32	     300	    D8s_v3	      €0.37	        €111	    €290
           PRF	Base de données reporting	        32	    64	     300	    F32s_v3	      €1.23	        €369	    €0
           PRD	Base de données reporting	        32	    64	     730	    F32s_v3	      €1.23	        €898	    €343
           
           it's important to understand the difference between VCPU and Core in the CPU column. That is crucial to calculate the VM Gabarit.
              For example, the VM Gabarit for the VM "Base de données transactionnelle" is D8s_v3, which has 8 Vcpu.
              
          A VCPU (Virtual Central Processing Unit) represents a share or a slice of a physical CPU that is assigned to a virtual machine (VM).
          It's a way of sharing the resources of a physical CPU among multiple VMs.  
         On the other hand, a Core represents a physical CPU on the host machine. Each Core can run one or more threads, depending on the technology of the CPU.  
           In the context of our app, the VM Gabarit column refers to the configuration of the virtual machine, including the number of VCPUs
             and the amount of RAM. The VM Gabarit is a suggestion from the {cloud_provider}'s VM templates, considering CPU and RAM.

           for the Disk table, the columns are: ENV          VM            Disk size(Go)        Disk type     Cost

           Cost is the month cost of the Disk taking account the disk size and the the disk type in azure public price

           As result, the Disk table looks like this:

           ENV	        VM	                            Disk Size (Go)	    Disk1 Ttype	    Disk1 Cost
           REC	    Base de données transactionnelle	    4000	        Standard_HDD	    €130
           PRF	    Base de données transactionnelle	    4000	        Premium_SSD	        €433
           PRD	    Base de données transactionnelle	    4000	        Premium_SSD	        €433
           REC	    Base de données reporting	            4000	        Standard_HDD	    €130
           PRF	    Base de données reporting	            4000	        Premium_SSD	        €433
           PRd	    Base de données reporting	            4000	        Premium_SSD	        €433


            After summarizing the data, your tables should look like this:

            Virtual Machines:
            | Environment | VM Name                  | Gabarit   | Hours/Month | VM Cost (€) |
            |-------------|--------------------------|-----------|-------------|-------------|
            | PRD         | Base de données reporting| F32s_v3   | 730         | €898        |
            | PRD         | Base de données transact.| M32ms     | 730         | €4,964      |
            | PRD         | Serveur de reporting SSRS| D16s_v3   | 730         | €533        |
            | PRF         | Base de données reporting| F32s_v3   | 300         | €369        |
            | PRF         | Base de données transact.| M32ms     | 300         | €2,040      |
            | PRF         | Serveur de reporting SSRS| D16s_v3   | 300         | €219        |
            | REC         | Base de données reporting| D8s_v3    | 300         | €111        |
            | REC         | Base de données transact.| D8s_v3    | 300         | €111        |
            |Total        |                          |           |             | €9,245      |

            Disks:
            | Environment | VM Name             | Disk Type    | Disk Size (GB) | Disk Cost (€) |
            |-------------|---------------------|--------------|----------------|---------------|
            | PRD         | Base de données rep.| Premium_SSD  | 4000           | €433          |
            | PRD         | Base de données trans.| Premium_SSD | 4000          | €433          |
            | PRF         | Base de données rep.| Premium_SSD  | 4000           | €433          |
            | PRF         | Base de données trans.| Premium_SSD | 4000          | €433          |
            | REC         | Base de données rep.| Standard_HDD | 4000           | €130          |
            | REC         | Base de données trans.| Standard_HDD| 4000          | €130          |
            |Total        |                     |              |                | €1,995        |
            this example is for Azure, but you should be able to do the same for GCP.

            Here is the provided information about the app's requirements:
            {app_requirements}

            based on the information above , your task is to do the budget of the app using {cloud_provider}'s public pricing.
            All the outputs HAVE TO BE in table format and the table have to be in markdown format
            put the hourly cost of the VM in the VM table 
            Your task extends beyond basic budgeting; you must also consider and incorporate cost optimization strategies. 
            Reserved Instances, Savings Plans on Azure, and Committed Use Discounts (CUD) on Google Cloud can substantially reduce costs. 
            for reserved instances and cud the term should be 3 years.
            If you opt for these strategies, the budget calculation must reflect the discounted pricing, leading to overall cost reduction.
            If you opt for these, the budget calculation will need to incorporate the discounted pricing, resulting in reduced overall expenses.
            you should calculate the total cost of each environment(dev, prf, prod),the total cost of each category, and the total cost of the application.
        '''
    cloud_provider = st.selectbox('Cloud Provider', ['Azure', 'GCP'])
    table_vm = tabulate(st.session_state.vms, headers="keys", tablefmt="grid")
    table_disk = tabulate(st.session_state.disks, headers="keys", tablefmt="grid")
    app_requirements = 'Pour les Machines Virtuelles' + table_vm + '\n' + 'Pour les Disques' + table_disk + '\n' + txt
    print(app_requirements)
    button = st.button('Submit')

    if button:
        prompt = PromptTemplate(
            input_variables=["app_requirements", "cloud_provider"],
            template=template,
        )

        final_prompt = prompt.format(app_requirements=app_requirements, cloud_provider=cloud_provider)

        llm = AzureChatOpenAI(deployment_name=st.secrets["OPENAI_DEPLOYMENT_NAME"],
                              model_name=st.secrets["OPENAI_MODEL_NAME"],
                              openai_api_base=st.secrets["OPENAI_DEPLOYMENT_ENDPOINT"],
                              openai_api_version=st.secrets["OPENAI_DEPLOYMENT_VERSION"],
                              openai_api_key=st.secrets["OPENAI_API_KEY"],
                              openai_api_type="azure")

        with get_openai_callback() as call_back:
            response = llm([
                HumanMessage(content=final_prompt)
            ])
            print(call_back)
        st.write(response.content)
        st.write(call_back)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()






