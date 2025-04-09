dt_ddmmyy="$(date '+%d-%m-%y')";
wget https://api-qcon.quantum.ibm.com/api/backends/ibm_osaka/properties -O $dt_ddmmyy.json;