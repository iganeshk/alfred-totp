require "json"

module ATotp
  VERSION = "0.1.2"
  ENV["PATH"] = "/usr/local/bin:/usr/bin"

  # This could possibly be cached.
  def self.ids
    # Getting key: https://apple.stackexchange.com/questions/276548/list-all-keys-added-to-keychain-using-security-add-generic-password
    `security dump-keychain alfred-totp.keychain | grep 0x00000007 | awk -F= '{print $2}' | tr -d \'"'`.strip.split("\n")
  end

  def self.gen_code(pass)
    io = IO::Memory.new
    Process.run("oathtool", ["--totp", "-b", pass], output: io)
    io.to_s.strip
  end

  def self.get_pass(id)
    io = IO::Memory.new
    Process.run("security", ["find-generic-password", "-s", id, "-w", "alfred-totp.keychain"], output: io)
    io.to_s.strip
  end

  def self.alfred_out
    ids.map do |id|
      pass = get_pass id
      code = gen_code pass
      workflow_path = Dir.current
      if File.exists?("#{workflow_path}/icons/#{id}.png")
        alfred_icon = "#{workflow_path}/icons/#{id}.png"
      else
        alfred_icon = "#{workflow_path}/icon.png"
      end
      {
        uid:      id,
        title:    id,
        subtitle: code,
        arg:      pass,
        icon:     {
          path: "#{alfred_icon}",
        },
        mods: {
          alt: {
            valid:    true,
            subtitle: "copy #{code}",
            arg:      pass,
          },
        },
      }
    end
  end

  print({rerun: 1, items: alfred_out}.to_json)
end
