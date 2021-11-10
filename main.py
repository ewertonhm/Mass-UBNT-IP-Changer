import ubnt
import time
import os
import sys
import configs
import configparser
import json


def main():

    config_auth = configparser.ConfigParser()
    config_hosts = configparser.ConfigParser()

    config_auth.read(configs.find_path() + "auth.ini")
    config_hosts.read(configs.find_path() + "hosts.ini")

    hosts = json.loads(config_hosts.get("HOSTS","hosts"))

    users = json.loads(config_auth.get('AUTH','users'))
    passwords = json.loads(config_auth.get('AUTH','passwords'))

    counter = 0

    for host in hosts:
        u = ubnt.Ubnt(host['ip'], host['port'])

        trys = 1
        configs.write_to_log('Tentando conectar ao host {0} porta {1} ... tentativa {2}/5'.format(host['ip'], host['port'], trys))
        trys = 2
        while not u.test_conn():
            configs.write_to_log('Tentando conectar ao host {0} porta {1} ... tentativa {2}/5'.format(host['ip'], host['port'], trys))
            trys = trys + 1
            if trys > 5:
                configs.write_to_fail(str(host['ip'] + ' - connection'))
                configs.write_to_log('Número máximo de tentativas sem sucesso atingido, passando para o próximo host.')
                break
            time.sleep(3)

        if u.test_conn():
            configs.write_to_log('Conectado com sucesso ao host {0} porta {1}'.format(host['ip'], host['port']))
            logged = False
            default = False
            for user in users:
                for password in passwords:
                    configs.write_to_log('Tentativa de login como {0}/{1}'.format(user, password))
                    if (u.do_login(user, password)):
                        configs.write_to_log('Login efetuado com sucesso!')
                        logged = True
                        if password == 'ubnt':
                            default = True
                    if logged:
                        break
                if logged:
                    break
            if default:
                configs.write_to_log("You are using the default Administrator password, changing!")
                u.change_defautl_password()
            if not logged:
                configs.write_to_log("Não foi possível acessar, verificar senhas!")
                configs.write_to_fail(str(host['ip'] + ' - password'))
            else:
                configs.write_to_log('Configurações de rede atuais:')
                u.get_network_configs()
                configs.write_to_log('Alterando para:')
                configs.write_to_log('IP Address: ' + host['new_ip'])
                configs.write_to_log('Netmask: ' + host['new_mask'])
                configs.write_to_log('Gateway IP: ' + host['new_gateway'])
                u.set_network_configs(host['new_ip'],host['new_mask'],host['new_gateway'])
                configs.write_to_sucess(host['ip'])
        counter = counter+1
        time.sleep(3)
        u.kill_driver()

if __name__ == '__main__':
    main()

