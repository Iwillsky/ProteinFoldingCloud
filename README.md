# ProteinFoldingCloud

Build Protein Folding as Service on Azure Cloud

![image](https://github.com/Iwillsky/ProteinFoldingCloud/blob/main/img/HackTeamLogo.png)

(Sponsored by MS Hackathon-2021 Program)

License of RoseTTAFold follow the [link](https://github.com/Iwillsky/ProteinFoldingCloud/blob/main/hpc/LICENSE)

### Teams

Thanks contribution from Hackathon teammates during Sep-Oct, 2021

### Architecture

![image](https://github.com/Iwillsky/ProteinFoldingCloud/blob/main/img/ArchProteinFolding_v2.jpg)

### Job Flow

"Submit a fasta squence file" 

  --> Automatic running in backend HPC cluster 
 
  --> "Get result PDB protein foloding result"

Protein-Folding-as-a-Service Protal : [link](https://aaron52077.wixsite.com/website-3/live-demo)

NOTICE: Due to backend resource cost charging, automatically job picking up is off by default. If you want to have a try please contact through this channel or mailto: iwillsky@163.com

### Repo Structure

· Web -- UI Interface for job submission 

· Data -- Scripts of job polling connection and result pushing (currently using CosmosDB as accounting database)

· HPC -- RoseTTAFold branch repo with parallelism enabled



### Samples

![image](https://github.com/Iwillsky/ProteinFoldingCloud/blob/main/img/model_O94985.png)


## Long Term consideration

Accommodate AlphaFold2 and MS-SAMF framework in plan



