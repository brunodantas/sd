installing thrift:
download, extract: http://www.apache.org/dyn/closer.cgi?path=/thrift/0.10.0/thrift-0.10.0.tar.gz
./configure
sudo make
sudo make install
sudo apt-get install python-all python-all-dev python-all-dbg


generate files from thrift:
thrift -r --gen py a.thrift


rwlock implementation took from https://majid.info/blog/a-reader-writer-lock-for-python