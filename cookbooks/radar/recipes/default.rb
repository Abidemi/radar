package 'epel-release' do
  action :install
end

package 'vim' do
  action :install
end

package 'git' do
  action :install
end

include_recipe 'radar::iptables'
include_recipe 'radar::user'
include_recipe 'radar::db'
include_recipe 'radar::api'
include_recipe 'radar::client'
include_recipe 'radar::web'
