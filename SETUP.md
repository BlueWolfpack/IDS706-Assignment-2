# environment setup
- Python 3.11+ from <https://www.python.org/downloads/> — check **Add python.exe to PATH**
- Java 17 (Temurin is fine): <https://adoptium.net/>
- Git for Windows: <https://git-scm.com/download/win>
- VS Code: <https://code.visualstudio.com/> — then install the *Python* and *Jupyter* extensions

Everything is run in bash except where noted

## close the terminal, open a new one and run:
rustc --version
cargo --version
java -version
python --version

## In the project folder
ensure that the "Scripts" subfolder includes download_data.py and prepare_data.py

python -m venv .venv
.venv\\Scripts\\python -m pip install --upgrade pip
.venv\\Scripts\\python -m pip install -e .
.venv\\Scripts\\python -m ipykernel install --user --name dataframe-engine-benchmark --display-name "Dataframe Engines"
.venv\\Scripts\\python scripts/download_data.py
.venv\\Scripts\\python scripts/prepare_data.py

## Rust Jyputer kernel run:
cargo install evcxr_jupyter
evcxr_jupyter --install

## Opening project
open project in VSCode and determine which kernel to select

## Verification run:
python --version
java -version
rustc --version
cargo --version
.venv\\Scripts\\python -m jupyter kernelspec list

### Ensure that: 
`kernelspec list` must include **Dataframe Engines** (`dataframe-engine-benchmark`) and **Rust** (`rust`).

Then confirm the Rust kernel actually runs (not Python). This must print `Hello from Rust.` If `evcxr` is not found, use the full path: `%USERPROFILE%\.cargo\bin\evcxr.exe` 

```powershell
"println!(`"Hello from Rust.`");" | evcxr
```