# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "raring-i386"
  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/raring/current" \
    "/raring-server-cloudimg-i386-vagrant-disk1.box"

  config.vm.network :forwarded_port, guest: 8001, host: 8001

  config.vm.provision :ansible do |ansible|
    ansible.playbook = "vagrant/playbook.yml"
    ansible.sudo = true
  end
end


# Hack for using ansible without private network - there's a patched version
# of the plugin bundled
require File.expand_path("../vagrant/ansible_plugin/plugin", __FILE__)
