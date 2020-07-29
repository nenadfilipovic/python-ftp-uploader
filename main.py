import os
from ftplib import FTP_TLS, error_perm
import checksumdir

ftp_client = FTP_TLS('host')
ftp_client.login('username', 'password')

print("\nConnected to: ", ftp_client.host, ":", ftp_client.port, "\n")


class FTPUploader:
    def __init__(self):
        pass

    def upload(self, path):
        for item in os.listdir(path):
            currentpath = os.path.join(path, item)
            if os.path.isfile(currentpath):
                print("Uploading file...: \n", item, "\n")
                ftp_client.storbinary('STOR ' + item, open(currentpath, 'rb'))
            elif os.path.isdir(currentpath):
                print("Creating directory...: \n", item, "\n")
                try:
                    ftp_client.mkd(item)
                except error_perm as e:
                    if not e.args[0].startswith('550'):
                        raise
                print("Current directory...: \n", item, "\n")
                ftp_client.cwd(item)
                self.upload(currentpath)
                print("Changing directory...: \n", currentpath, "\n")
                ftp_client.cwd("..")

    def hash(self, directory):
        if 'md5hash.txt' in os.listdir(os.getcwd()):
            print("Rehashing directory.\n")
            md5hash = checksumdir.dirhash(directory)
            with open('md5hash.txt', 'r') as file:
                data = file.read()
            if md5hash != data:
                print("Changes spotted, now uploading.\n")
                with open("md5hash.txt", 'w') as outfile:
                    outfile.write(md5hash)
                self.upload(directory)
            else:
                print("No changes in directory detected.\n")
        else:
            print("Hashing directory.\n")
            md5hash = checksumdir.dirhash(directory)
            with open("md5hash.txt", 'w') as outfile:
                outfile.write(md5hash)
            print("Directory hashed, now uploading.\n")
            self.upload(directory)

    def menu(self):
        print("Welcome, choose one option:\n")
        print("1. List all files from server.\n")
        print("2. Upload files to server.\n")
        print("3. Quit.\n")
        choise = input()
        if choise == '1':
            ftp_client.cwd('httpdocs')
            ftp_client.retrlines('LIST')
            ftp_client.cwd('..')
            print("\nReturn to menu? (y or n)")
            input_return = input()
            if input_return == "y":
                self.menu()
            else:
                print("Quiting...")
                quit()
        elif choise == '2':
            print("Set your directory name: (Directory should be in relative path to this script.)\n")
            directory = input()
            print("This is root of your directory: ", os.listdir(directory), "Do you want to proceed? (y or n)\n")
            input_return = input()
            if input_return == "y":
                self.hash(directory)
            print("Return to menu? (y or n)\n")
            input_return = input()
            if input_return == "y":
                self.menu()
            else:
                print("Quiting...")
                quit()
        elif choise == '3':
            print("Quiting...")
            quit()
        else:
            print("That menu item doesnt exist.\n")
            self.menu()


o = FTPUploader()
o.menu()
ftp_client.quit()
