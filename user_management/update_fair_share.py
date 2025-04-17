import os


def main():
    with open("advisors.csv", "r") as file:
        headers = file.readline().strip().split(",")
        for line in file:
            row = line.strip().split(",")
            advisor = row[headers.index("advisor")]
            email = row[headers.index("email")]
            group = row[headers.index("group")]
            share = 4
            if group == "founder":
                share = 14
            if email == "tbl@cin.ufpe.br":
                share = 52
            if email == "fatc@cin.ufpe.br":
                share = 26
            os.system(
                f"sudo sacctmgr -i add account {advisor}_group parent={group}s Fairshare={share}"
            )
    os.system("sacctmgr show assoc format=account,user,fairshare")


if __name__ == "__main__":
    main()
