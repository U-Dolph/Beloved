templates = {
"main.lua": '''require 'includes'

function love.load()

end

function love.update(dt)

end

function love.draw()

end

function love.keypressed(key)
    if key == 'escape' then
        love.event.quit(0)
    end
end
''',

"conf.lua": '''function love.conf(t)
    t.window.title = "{projectname}"
    t.window.width = 1280
    t.window.height = 720

    t.console = true
    t.window.resizable = true

    t.window.fullscreen = false
    t.window.vsync = 1
    t.window.msaa = 0
end
''',

"class.lua": '''local {class_name} = {{}}
{class_name}.__index = {class_name}

function {class_name}:new()
    local self = {{

    }}

    setmetatable(self, {class_name})
    return self
end

return {class_name}
''',

"includes.lua": '''''',

"beloved.conf": {
    "templates": None,
    "directories": ["ast", "gfx", "sfx", "lib", "sdr"],
    "files": ["main.lua", "conf.lua", "includes.lua"],
    "libraries_folder": "<LIBRARIES_PATH>",
    "build_directory": ".build",
    "love_output": "love",
    "build_output": "bin"
}
}