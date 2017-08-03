distributed graph database server using thrift + replication via PySyncObj (based on raft protocol)


installing thrift:
download, extract: http://www.apache.org/dyn/closer.cgi?path=/thrift/0.10.0/thrift-0.10.0.tar.gz
./configure
sudo make
sudo make install
sudo apt-get install python-all python-all-dev python-all-dbg

generate files from thrift:
thrift -r --gen py a.thrift


running:
> . init_servers.sh {cluster_qty} (set for 3 replicated servers)
> python3 client.py {port_num} (9000 <= port_num <= 9000 + server_qty)


ex_filmebook initializes an example database
> python3 ex_filmebook.py {port_num}

filmebook is an example client
> python3 filmebook.py {port_num}


rwlock from https://majid.info/blog/a-reader-writer-lock-for-python
PySyncObj from https://github.com/bakwc/PySyncObj
