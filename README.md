# Instalação de Um Node do Cluster
## Passos
- Formatar Maquina e Configuração Inicial
- Instalar Drivers Nvidia
- Instalar Munge
- Instalar Slurm
- Instalar Lmod
- Instalar EasyBuild
- Instalar Softwares Pelo Easybuild
- Configurar Modules


## Formatação da Maquina

- Instalado Ubuntu 22.04 com SSH
- Configurado Realm para login com domínio
- Ponto de montagem home compartilhado (install nfs-common, criar diretório /home/CIN e montar)
- Permissão no arquivo sudoers

## Atualizar Repositorios e Pacotes

```bash
sudo apt update
sudo apt upgrade
```

## Instalar Drivers Nvidia
Nós `cluster-node[1-5]` possuem placas de vídeo `Nvidia RTX 3090`, Nós `cluster-node[6-10]` possuem placas de vídeo `Nvidia A100`.
```bash
sudo apt install nvidia-driver-525-server libnvidia-ml-dev
```
- Foi fixado a versão 525
- O pacote libnvidia-ml-dev é utilizado pelo slurm para dar suporte ao nvml

## Instalar Munge
```bash
sudo apt install munge libmunge-dev
sudo cp arquivos/munge.key /etc/munge/munge.key
sudo systemctl enable munge
sudo systemctl start munge
```

## Instalar Slurm
```bash
sudo apt install build-essential libhwloc-dev libdbus-1-dev libssl-dev libibverbs-dev
sudo addgroup --gid 64030 slurm
sudo useradd -s /usr/sbin/nologin --home /nonexistent -M -u 64030 -g 64030 slurm
sudo mkdir /tmp/slurmd
wget https://download.schedmd.com/slurm/slurm-22.05.3.tar.bz2
tar -xvf slurm-22.05.3.tar.bz2
cd slurm-22.05.3
./configure
sudo make install -j 60
sudo cp etc/slurmd.service /etc/systemd/system/slurmd.service
```
#### Copiar configs e habilitar serviço
```bash
sudo cp arquivos/slurm.conf /usr/local/etc/slurm.conf
sudo cp arquivos/gres.conf /usr/local/etc/gres.conf
sudo cp arquivos/cgroup.conf /usr/local/etc/cgroup.conf
sudo systemctl enable slurmd
sudo systemctl start slurmd
```

## Instalar Lmod
```bash
sudo apt install tcl8.6 tcl8.6-dev zip lua5.4 liblua5.4-dev luarocks lua-filesystem
sudo luarocks install luaposix
wget https://github.com/TACC/Lmod/archive/refs/tags/8.7.22.tar.gz
tar xfz 8.7.22.tar.gz
cd Lmod-8.7.22/
./configure --prefix=/opt
sudo make install -j60
sudo ln -s /opt/lmod/lmod/init/profile /etc/profile.d/z00_lmod.sh
sudo ln -s /opt/lmod/lmod/init/cshrc /etc/profile.d/z00_lmod.csh
```

#### Adicionar seguintes linhas no /etc/bash.bashrc:
```text
# Enable bash module support
. /opt/lmod/lmod/init/profile >/dev/null
```

## Instalar EasyBuild
```bash
sudo apt install python3-pip
sudo python3 -m pip install easybuild
sudo mkdir /opt/easybuild
sudo chmod 777 /opt/easybuild
sudo cp arquivos/eb.cf /opt/easybuild/eb.cf
sudo cp -r arquivos/custom-ebs /opt/easybuild/custom-ebs
```
#### Instalar Softwares Pelo Easybuild
- Python 3.10.8, 3.9.6 e 3.8.6
- Xvfb 21.1.6
- freeglut 3.2.2
```bash
eb --configfile=/opt/easybuild/eb.cf UnZip-6.0.eb -r
eb --configfile=/opt/easybuild/eb.cf /opt/easybuild/custom-ebs/Python-3.10.8-GCCcore-12.2.0.eb -r
eb --configfile=/opt/easybuild/eb.cf /opt/easybuild/custom-ebs/Python-3.9.6-GCCcore-12.2.0.eb -r
eb --configfile=/opt/easybuild/eb.cf /opt/easybuild/custom-ebs/Python-3.8.6-GCCcore-12.2.0.eb -r
eb --configfile=/opt/easybuild/eb.cf Xvfb-21.1.6-GCCcore-12.2.0.eb -r
sudo wget https://github.com/FreeGLUTProject/freeglut/releases/download/v3.2.2/freeglut-3.2.2.tar.gz -P /opt/easybuild/custom-ebs
eb --configfile=/opt/easybuild/eb.cf /opt/easybuild/custom-ebs/freeglut-3.2.2-GCCcore-12.2.0.eb -r
```

## Configurar Modules
#### Criar links symbolicos para os modules instalados no Path do Lmod
```bash
sudo mkdir -p /opt/modulefiles/Core/Python /opt/modulefiles/Core/Xvfb
sudo ln -s /opt/easybuild/modules/all/Python/3.10.8-GCCcore-12.2.0.lua /opt/modulefiles/Core/Python/
sudo ln -s /opt/easybuild/modules/all/Python/3.9.6-GCCcore-12.2.0.lua /opt/modulefiles/Core/Python/
sudo ln -s /opt/easybuild/modules/all/Python/3.8.6-GCCcore-12.2.0.lua /opt/modulefiles/Core/Python/
sudo ln -s /opt/easybuild/modules/all/Xvfb/21.1.6-GCCcore-12.2.0.lua /opt/modulefiles/Core/Xvfb/
sudo mkdir -p /opt/modulefiles/Linux/Brotli /opt/modulefiles/Linux/Mesa /opt/modulefiles/Linux/X11 /opt/modulefiles/Linux/expat /opt/modulefiles/Linux/libdrm /opt/modulefiles/Linux/libpng /opt/modulefiles/Linux/ncurses /opt/modulefiles/Linux/xorg-macros /opt/modulefiles/Linux/GCCcore /opt/modulefiles/Linux/OpenSSL /opt/modulefiles/Linux/XZ /opt/modulefiles/Linux/fontconfig /opt/modulefiles/Linux/libffi /opt/modulefiles/Linux/libreadline /opt/modulefiles/Linux/nettle /opt/modulefiles/Linux/zlib /opt/modulefiles/Linux/GMP /opt/modulefiles/Linux/SQLite /opt/modulefiles/Linux/binutils /opt/modulefiles/Linux/freetype /opt/modulefiles/Linux/libglvnd /opt/modulefiles/Linux/libunwind /opt/modulefiles/Linux/pixman /opt/modulefiles/Linux/zstd /opt/modulefiles/Linux/LLVM /opt/modulefiles/Linux/Tcl /opt/modulefiles/Linux/bzip2 /opt/modulefiles/Linux/gzip /opt/modulefiles/Linux/libpciaccess /opt/modulefiles/Linux/lz4 /opt/modulefiles/Linux/util-linux
sudo ln -s /opt/easybuild/modules/all/libffi/3.4.4-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libffi/
sudo ln -s /opt/easybuild/modules/all/libreadline/8.2-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libreadline/
sudo ln -s /opt/easybuild/modules/all/XZ/5.2.7-GCCcore-12.2.0.lua /opt/modulefiles/Linux/XZ/
sudo ln -s /opt/easybuild/modules/all/OpenSSL/1.1.lua /opt/modulefiles/Linux/OpenSSL/
sudo ln -s /opt/easybuild/modules/all/ncurses/6.3-GCCcore-12.2.0.lua /opt/modulefiles/Linux/ncurses/
sudo ln -s /opt/easybuild/modules/all/bzip2/1.0.8-GCCcore-12.2.0.lua /opt/modulefiles/Linux/bzip2/
sudo ln -s /opt/easybuild/modules/all/binutils/2.39-GCCcore-12.2.0.lua /opt/modulefiles/Linux/binutils/
sudo ln -s /opt/easybuild/modules/all/GCCcore/12.2.0.lua /opt/modulefiles/Linux/GCCcore/
sudo ln -s /opt/easybuild/modules/all/SQLite/3.39.4-GCCcore-12.2.0.lua /opt/modulefiles/Linux/SQLite/
sudo ln -s /opt/easybuild/modules/all/GMP/6.2.1-GCCcore-12.2.0.lua /opt/modulefiles/Linux/GMP/
sudo ln -s /opt/easybuild/modules/all/Tcl/8.6.12-GCCcore-12.2.0.lua /opt/modulefiles/Linux/Tcl/
sudo ln -s /opt/easybuild/modules/all/zlib/1.2.12-GCCcore-12.2.0.lua /opt/modulefiles/Linux/zlib/
sudo ln -s /opt/easybuild/modules/all/nettle/3.8.1-GCCcore-12.2.0.lua /opt/modulefiles/Linux/nettle/
sudo ln -s /opt/easybuild/modules/all/X11/20221110-GCCcore-12.2.0.lua /opt/modulefiles/Linux/X11/
sudo ln -s /opt/easybuild/modules/all/pixman/0.42.2-GCCcore-12.2.0.lua /opt/modulefiles/Linux/pixman/
sudo ln -s /opt/easybuild/modules/all/libdrm/2.4.114-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libdrm/
sudo ln -s /opt/easybuild/modules/all/libunwind/1.6.2-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libunwind/
sudo ln -s /opt/easybuild/modules/all/Mesa/22.2.4-GCCcore-12.2.0.lua /opt/modulefiles/Linux/Mesa/
sudo ln -s /opt/easybuild/modules/all/xorg-macros/1.19.3-GCCcore-12.2.0.lua /opt/modulefiles/Linux/xorg-macros/
sudo ln -s /opt/easybuild/modules/all/freetype/2.12.1-GCCcore-12.2.0.lua /opt/modulefiles/Linux/freetype/
sudo ln -s /opt/easybuild/modules/all/libglvnd/1.6.0-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libglvnd/
sudo ln -s /opt/easybuild/modules/all/libpciaccess/0.17-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libpciaccess/
sudo ln -s /opt/easybuild/modules/all/fontconfig/2.14.1-GCCcore-12.2.0.lua /opt/modulefiles/Linux/fontconfig/
sudo ln -s /opt/easybuild/modules/all/LLVM/15.0.5-GCCcore-12.2.0.lua /opt/modulefiles/Linux/LLVM/
sudo ln -s /opt/easybuild/modules/all/zstd/1.5.2-GCCcore-12.2.0.lua /opt/modulefiles/Linux/zstd/
sudo ln -s /opt/easybuild/modules/all/lz4/1.9.4-GCCcore-12.2.0.lua /opt/modulefiles/Linux/lz4/
sudo ln -s /opt/easybuild/modules/all/gzip/1.12-GCCcore-12.2.0.lua /opt/modulefiles/Linux/gzip/
sudo ln -s /opt/easybuild/modules/all/libpng/1.6.38-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libpng/
sudo ln -s /opt/easybuild/modules/all/util-linux/2.38.1-GCCcore-12.2.0.lua /opt/modulefiles/Linux/util-linux/
sudo ln -s /opt/easybuild/modules/all/Brotli/1.0.9-GCCcore-12.2.0.lua /opt/modulefiles/Linux/Brotli/
sudo ln -s /opt/easybuild/modules/all/expat/2.4.9-GCCcore-12.2.0.lua /opt/modulefiles/Linux/expat/
sudo mkdir /opt/modulefiles/Core/freeglut /opt/modulefiles/Linux/libGLU
sudo ln -s /opt/easybuild/modules/all/freeglut/3.2.2-GCCcore-12.2.0.lua /opt/modulefiles/Core/freeglut/
sudo ln -s /opt/easybuild/modules/all/libGLU/9.0.2-GCCcore-12.2.0.lua /opt/modulefiles/Linux/libGLU/
```
#### Copiar configs do modules
```bash
sudo cp arquivos/lmod-core.modulerc.lua /opt/lmod/lmod/modulefiles/Core/.modulerc.lua
sudo cp arquivos/core.modulerc.lua /opt/modulefiles/Core/.modulerc.lua
sudo cp arquivos/linux.modulerc.lua /opt/modulefiles/Linux/.modulerc.lua
```

# Instalação do nodo de base de dados do Slurm
Para armazenar associações no Slurm é necessário utilizar uma bases de dados. Nesta seção serão apresentados os passos necessários para instalar e configurar o MySQL server e o Daemon Slurmdbd corretamente.

## MySQL server 

Instalar e iniciar o MySQL server

```bash
sudo apt-get install libmysqlclient-dev mysql-server
sudo service mysql start
sudo service mysql enable
sudo service mysql status
```

Fazer o login no prompt de comando do MySQL

```bash
sudo mysql
```

Configurar o acesso do slurm à base de dados

```
create database slurm_acct_db;
create user 'slurm'@'localhost’;
set password for 'slurm'@'localhost' = 'insert_passwd';
grant usage on *.* to 'slurm'@'localhost';
grant all privileges on slurm_acct_db.* to 'slurm'@'localhost';
flush privileges;
```

Verificar suporte ao InnoDB e se a base de dados do slurm (slurm_acct_db) foi criada

```bash
show engines;
show databases;
quit
```

## Configuração do dameon SlurmDBD 

Criar usuários ‘munge’ e ‘slurm’ e sincronizar os respectivos uids e gids. Após instalar o Munge, deve-se configurar os seguintes arquivos e permissões.

```bash
sudo cp /slurm-22.05.3/etc/slurmdbd.service /etc/systemd/system
sudo cp arquivos/slurmdbd.conf /usr/local/etc/slurmdbd.conf
sudo chown slurm: /usr/local/etc/slurmdbd.conf
sudo chmod 600 /usr/local/etc/slurmdbd.conf
sudo mkdir /var/log/slurm
sudo touch /var/log/slurm/slurmdbd.log
sudo chown slurm: /var/log/slurm/slurmdbd.log
```

Iniciar slurmdbd
```bash
systemctl start slurmdbd
systemctl enable slurmdbd
sudo scontrol reconfigure
```
