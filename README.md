Planning board:

base_url = https://monarch-initiative.org/api

nodes:  
- <s>base_url/entity/{id}</s>  
- base_url/entity/{id}/{type of node}

edges:          
- ~~base_url/association/{id}~~
- base_url/association/type/{association_type}  
- base_url/association/to/{object}  
- base_url/association/from/{subject}  
- base_url/association/between/{subject}/{object}  
- base_url/association/find/{subject_category}  
- base_url/association/find/{subject_category}/{object_category} 
