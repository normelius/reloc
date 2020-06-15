# Reloc

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![GitHub license](https://img.shields.io/github/license/Naereen/StrapDown.js.svg)](https://github.com/Naereen/StrapDown.js/blob/master/LICENSE)

## Features
* Serves as a simple file transfer service between client and server. Initially designed for easy transfer of files to single-board computers, such as the Raspberry Pi.
* Can be used both locally on the network or externally over the internet.
* Reloc can be used as a command-line application for easier transfer of files from the command prompt.

 
## Installation
```bash
$ pip3 install reloc
```
 
## Usage
#### Server-side
Start server where you want to receive files. If no path is specified the home folder is used. Two modes of the server can be used; internal or external. By using the internal mode, only connection over the local network is possible. By using external mode, connection to the server can be made over the internet if the specified port is open in the network.


```python
import reloc

# Starting server to handle external connections, i.e. over the internet.
server = reloc.server(mode = 'external', host = '92.34.13.274', 
    port = 1750, def_path = '/users/antonnormelius/documents')

# Start listening for incoming data stream.
server.receive()
```
 
#### Client-side
Client is used to transfer files and folders to server. Observe that
the host and port for the client need to be the same as the host and port
for the server. 
```python
import reloc

# Connecting to external server.
client = reloc.client(host = '92.34.13.274', port = 1750)

# Sending a text file.
filename = 'test.txt'
client.transmit(filename)

# Sending a folder.
foldername = 'test'
client.transmit(foldername)

# Disconnect from the client.
client.disconnect()

```

#### Command-Line Application
Reloc can be used as a command-line application in order to transfer files to the server
using the command prompt, i.e. terminal.

###### Internal transfer, i.e. over local network.
```bash
$ reloc internal file.txt
$ reloc internal folder
```

###### External transfer, i.e. over the internet.
Observe that both host and port needs to be specified in order
to transfer files in external mode.
```bash
$ reloc external file.txt --host 92.34.13.274 --port 1750
$ reloc external folder --host 92.34.13.274 --port 1750
```

## Releases
* 0.0.2 - Initial stable release.

## License
[MIT](https://choosealicense.com/licenses/mit/)
