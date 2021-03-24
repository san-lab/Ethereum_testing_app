## Information about the testing environment.
### Accounts inside AKV
- Acount1: "0x71217b5145aad63387673A39a717e5d2aABD6c5B"
- Key1 name on AKV: "santander"
- Acount2: "0xa38D7EE6Ea7Ba8503Bb9A51a15e959371eEedFa2"
- Key2 name on AKV: "bankia"
- Acount3: "0x8B7aa6dCefFCb2917Bc18609a8E1E650F038980A"
- Key3 name on AKV: "bbva"
- Acount3: "0x145dc3442412EdC113b01b63e14e85BA99926830"
- Key4 name on AKV: "hsm-key"

### Local accounts
- Local 1:"0x715597ecADA60aB6B5F93778F24cF4fA121822f4"
- Local 2:"0x85D37067d6a53f217Fb9100fDc575D807140A33c"
- Local 3:"0x5DF55Ed20FbF6bd788F86d780878b1c4B22E8d7e"
- Local 4:"0x49453eb8866225b92a38367b85de002f1d9244d1"

## Usage of the aplication
The file that needs to be executed is akv_ethereum_signing.py. These would be an example of execution of the application.
```
python3 akv_ethereum_signing.py <num_executions> <task> <mode> (<num_threads>)
```
As you can see the execution accepts 4 parameters.
- num_executions: Used to specify the total number of calls to AKV if executed in multithread mode it refers to the total number of execution not the number of executions per thread.
- task: It can be either get (which just does the get of the key from AKV), sign (which caches the key on the first call and then only signs transactions) or both (which instead of caching the key, asks for it before each sign transaction).
- mode: This is used to specify one thread or many with the keywords (single, multi)
- num_threads: This last argument is only used in multithread to specify the number of threads of the execution.

## Note
If you get any errors when installing the secp256k1.
Try to execute
```
sudo apt install libsecp256k1-dev
```
to install the dev version of the underlining library.
After that try again to install the dependencies.