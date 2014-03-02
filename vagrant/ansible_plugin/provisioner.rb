require "tempfile"

module VagrantPlugins
  module Ansible
    class Provisioner < Vagrant.plugin("2", :provisioner)
      def provision
        ssh = @machine.ssh_info

        options = %W[--private-key=#{ssh[:private_key_path]} --user=#{ssh[:username]}]
        options << "--extra-vars=" + config.extra_vars.map{|k,v| "#{k}=#{v}"}.join(' ') if config.extra_vars
        options << "--ask-sudo-pass" if config.ask_sudo_pass

        if config.inventory_file
            options << "--inventory-file=#{config.inventory_file}"
        else
            inventory_file = Tempfile.open("vagrant_ansible_inventory") do |f|
                f.write("#{@machine.name} ansible_ssh_host=#{ssh[:host]}" \
                        " ansible_ssh_port=#{ssh[:port]}")
                f
            end
            options << "--inventory-file=#{inventory_file.path}"
        end


        if config.limit
          if not config.limit.kind_of?(Array)
            config.limit = [config.limit]
          end
          config.limit = config.limit.join(",")
          options << "--limit=#{config.limit}"
        end

        options << "--sudo" if config.sudo
        options << "--sudo-user=#{config.sudo_user}" if config.sudo_user
        options << "--verbose" if config.verbose

        # Assemble the full ansible-playbook command
        command = (%w(ansible-playbook) << options << config.playbook).flatten

        # Write stdout and stderr data, since it's the regular Ansible output
        command << {
          :env => { "ANSIBLE_FORCE_COLOR" => "true" },
          :notify => [:stdout, :stderr]
        }

        begin
          Vagrant::Util::Subprocess.execute(*command) do |type, data|
            if type == :stdout || type == :stderr
              @machine.env.ui.info(data.chomp, :prefix => false)
            end
          end
        rescue Vagrant::Util::Subprocess::LaunchError
          raise Vagrant::Errors::AnsiblePlaybookAppNotFound
        # ensure
          # inventory_file.unlink if inventory_file
        end
      end
    end
  end
end
