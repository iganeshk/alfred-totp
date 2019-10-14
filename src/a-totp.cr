require "json"

module AlfredTOTP
  VERSION = "0.1.3"
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

  def self.get_steam_otp(pass)
    command = "python3 steam.py #{pass}"
    io = IO::Memory.new
    Process.run(command, shell: true, output: io)
    io.to_s.strip
  end

  def self.alfred_out
    ids.map do |id|
      # if service is steam, run it's script to get otp
      if id == "steam"
        pass = get_pass id
        code = get_steam_otp pass
      else
        pass = get_pass id
        code = gen_code pass
      end
      workflow_path = Dir.current
      if File.exists?("./icons/#{id}.png")
        alfred_icon = "./icons/#{id}.png"
      else
        alfred_icon = "./icon.png"
      end
      {
        uid:      id,
        title:    id,
        subtitle: code,
        arg:      code,
        icon:     {
          path: "#{alfred_icon}",
        },
        mods: {
          alt: {
            valid:    true,
            subtitle: "copy #{code}",
            arg:      code,
          },
        },
      }
    end
  end

  print({rerun: 1, items: alfred_out}.to_json)
end
