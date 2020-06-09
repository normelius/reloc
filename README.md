# Trado
## Observe that this is still under development and is being continuously updated.

## Features
* Serves as a simple file transfer service between client and server. Initially designed for easy transfer of files to single-board computers, such as the Raspberry Pi.
* Can be used both locally on the network or over the internet.

 
## Installation
```bash
Soon updated
```
 
## Usage
#### Server-side
Start server where you want to receive files. If no path is specified the home folder is used. Two modes of the server can be used; internal or external. By using the internal mode, only connection over the local network is possible.Bby using external mode, connection to the server can be made if the used port is open in the network.


```python
import trado

server = trado.trado()
# Connecting externally, i.e. connect over the internet.
server.connect_server(mode = 'external', host = '92.34.13.274', port = 1750,
    def_path = '/users/antonnormelius/documents')
server.receive()
```
 
#### Client-side
Client is used to transfer files and folders to server. Observe that
the host and port for the client need to be the same as the host and port
for the server. 
```python
import trado

client = trado.trado()
client.connect_client(host = '92.34.13.274', port = 1750)

# Sending a text file.
filename = 'test.txt'

# Sending a folder.
foldername = 'test'
client.transmit(foldername)

# Disconnect from the client.
client.disconnect()

```

## License
[MIT](https://choosealicense.com/licenses/mit/)
