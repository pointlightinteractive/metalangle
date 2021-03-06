#!/usr/bin/python
# Copyright 2019 The ANGLE Project Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.
#
# gen_mtl_internal_shaders.py:
#   Code generation for Metal backend's default shaders.
#   NOTE: don't run this script directly. Run scripts/run_code_generation.py.

import os
import sys
import json
from datetime import datetime

sys.path.append('../..')
import angle_format

template_header_boilerplate = """// GENERATED FILE - DO NOT EDIT.
// Generated by {script_name}
//
// Copyright {copyright_year} The ANGLE Project Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.
//
"""


# Convert content of a file to byte array and store in a header file.
# variable_name: name of C++ variable that will hold the file content as byte array.
# filename: the file whose content will be converted to C++ byte array.
# dest_src_file: destination header file that will contain the byte array.
def append_file_as_byte_array_string(variable_name, filename, dest_src_file):
    string = '// Generated from {0}:\n'.format(filename)
    string += 'constexpr uint8_t {0}[]={{\n'.format(variable_name)
    bytes_ = open(filename, "rb").read()
    for byte in bytes_:
        string += '0x{:02x}'.format(ord(byte)) + ", "
    string += "\n};\n"
    with open(dest_src_file, "a") as out_file:
        out_file.write(string)


# Compile metal shader.
# mac_version: target version of macOS
# ios_version: target version of iOS
# variable_name: name of C++ variable that will hold the compiled binary data as a C array.
# additional_flags: additional shader compiler flags
# src_files: metal source files
def gen_precompiled_shaders(mac_version, ios_version, variable_name, additional_flags, src_files):
    print('Generating default shaders with flags=\'{0}\' ...'.format(additional_flags))

    # Mac version's compilation
    print('Compiling macos {0} version of default shaders ...'.format(mac_version))
    object_files = ''
    for src_file in src_files:
        object_file = 'compiled/default.{0}.{1}.air'.format(mac_version, src_file)
        object_files += ' ' + object_file
        os.system('xcrun -sdk macosx metal -mmacosx-version-min={0} {1} {2} -c -o {3}'.format(
            mac_version, additional_flags, src_file, object_file))
    os.system(
        'xcrun -sdk macosx metallib {object_files} -o compiled/default.{mac_version}.metallib'
        .format(mac_version=mac_version, object_files=object_files))

    # iOS device version's compilation
    print('Compiling ios {0} version of default shaders ...'.format(ios_version))
    object_files = ''
    for src_file in src_files:
        object_file = 'compiled/default.ios.{0}.{1}.air'.format(ios_version, src_file)
        object_files += ' ' + object_file
        os.system('xcrun -sdk iphoneos metal -mios-version-min={0} {1} {2} -c -o {3}'.format(
            ios_version, additional_flags, src_file, object_file))
    os.system(
        'xcrun -sdk iphoneos metallib {object_files} -o compiled/default.ios.{ios_version}.metallib'
        .format(ios_version=ios_version, object_files=object_files))

    # iOS simulator version's compilation
    print('Compiling ios {0} simulator version of default shaders ...'.format(ios_version))
    object_files = ''
    object_files = ''
    for src_file in src_files:
        object_file = 'compiled/default.ios_sim.{0}.{1}.air'.format(ios_version, src_file)
        object_files += ' ' + object_file
        os.system('xcrun -sdk iphonesimulator metal {0} {1} -c -o {2}'.format(
            additional_flags, src_file, object_file))
    os.system(
        'xcrun -sdk iphonesimulator metallib {object_files} -o compiled/default.ios_sim.{ios_version}.metallib'
        .format(ios_version=ios_version, object_files=object_files))

    # tvOS device version's compilation
    print('Compiling tvos {0} version of default shaders ...'.format(ios_version))
    object_files = ''
    for src_file in src_files:
        object_file = 'compiled/default.tvos.{0}.{1}.air'.format(ios_version, src_file)
        object_files += ' ' + object_file
        os.system('xcrun -sdk appletvos metal -mtvos-version-min={0} {1} {2} -c -o {3}'.format(
            ios_version, additional_flags, src_file, object_file))
    os.system(
        'xcrun -sdk appletvos metallib {object_files} -o compiled/default.tvos.{ios_version}.metallib'
        .format(ios_version=ios_version, object_files=object_files))

    # tvOS simulator version's compilation
    print('Compiling tvos {0} simulator version of default shaders ...'.format(ios_version))
    object_files = ''
    object_files = ''
    for src_file in src_files:
        object_file = 'compiled/default.tvos_sim.{0}.{1}.air'.format(ios_version, src_file)
        object_files += ' ' + object_file
        os.system('xcrun -sdk appletvsimulator metal {0} {1} -c -o {2}'.format(
            additional_flags, src_file, object_file))
    os.system(
        'xcrun -sdk appletvsimulator metallib {object_files} -o compiled/default.tvos_sim.{ios_version}.metallib'
        .format(ios_version=ios_version, object_files=object_files))

    # Mac version's byte array string
    os.system(
        'echo "#if TARGET_OS_OSX || TARGET_OS_MACCATALYST\n" >> compiled/mtl_default_shaders.inc')
    append_file_as_byte_array_string(variable_name,
                                     'compiled/default.{0}.metallib'.format(mac_version),
                                     'compiled/mtl_default_shaders.inc')
    os.system('echo "constexpr size_t {0}_len=sizeof({0});" >> compiled/mtl_default_shaders.inc'
              .format(variable_name))

    # iOS simulator version's byte array string
    os.system(
        'echo "\n#elif TARGET_OS_IOS && TARGET_OS_SIMULATOR  // TARGET_OS_OSX || TARGET_OS_MACCATALYST\n" >> compiled/mtl_default_shaders.inc'
    )

    append_file_as_byte_array_string(variable_name,
                                     'compiled/default.ios_sim.{0}.metallib'.format(ios_version),
                                     'compiled/mtl_default_shaders.inc')
    os.system('echo "constexpr size_t {0}_len=sizeof({0});" >> compiled/mtl_default_shaders.inc'
              .format(variable_name))

    # iOS version's byte array string
    os.system(
        'echo "\n#elif TARGET_OS_IOS  // TARGET_OS_OSX || TARGET_OS_MACCATALYST\n" >> compiled/mtl_default_shaders.inc'
    )

    append_file_as_byte_array_string(variable_name,
                                     'compiled/default.ios.{0}.metallib'.format(ios_version),
                                     'compiled/mtl_default_shaders.inc')
    os.system('echo "constexpr size_t {0}_len=sizeof({0});" >> compiled/mtl_default_shaders.inc'
              .format(variable_name))

    # tvOS simulator version's byte array string
    os.system(
        'echo "\n#elif TARGET_OS_TV && TARGET_OS_SIMULATOR  // TARGET_OS_OSX || TARGET_OS_MACCATALYST\n" >> compiled/mtl_default_shaders.inc'
    )

    append_file_as_byte_array_string(variable_name,
                                     'compiled/default.tvos_sim.{0}.metallib'.format(ios_version),
                                     'compiled/mtl_default_shaders.inc')
    os.system('echo "constexpr size_t {0}_len=sizeof({0});" >> compiled/mtl_default_shaders.inc'
              .format(variable_name))

    # tvOS version's byte array string
    os.system(
        'echo "\n#elif TARGET_OS_TV  // TARGET_OS_OSX || TARGET_OS_MACCATALYST\n" >> compiled/mtl_default_shaders.inc'
    )

    append_file_as_byte_array_string(variable_name,
                                     'compiled/default.tvos.{0}.metallib'.format(ios_version),
                                     'compiled/mtl_default_shaders.inc')
    os.system('echo "constexpr size_t {0}_len=sizeof({0});" >> compiled/mtl_default_shaders.inc'
              .format(variable_name))

    os.system(
        'echo "#endif  // TARGET_OS_OSX || TARGET_OS_MACCATALYST\n" >> compiled/mtl_default_shaders.inc'
    )

    os.system('rm -rfv compiled/default.*')


def gen_shader_enums_code(angle_formats):

    code = "namespace rx\n"
    code += "{\n"
    code += "namespace mtl_shader\n"
    code += "{\n"
    code += "\n"
    code += "namespace FormatID\n"
    code += "{\n"
    code += "enum\n"
    code += "{\n"
    code += "    NONE,\n"
    for angle_format in sorted(angle_formats):
        if angle_format == 'NONE':  # NONE already moved to the beginning of enum declaration
            continue
        code += "    " + angle_format + ",\n"
    code += "};\n\n"
    code += "}\n"
    code += "\n"
    code += "}\n"
    code += "}\n"

    return code


def main():
    src_files = [
        'blit.metal', 'clear.metal', 'gen_indices.metal', 'gen_mipmap.metal', 'copy_buffer.metal',
        'visibility.metal'
    ]
    # auto_script parameters.
    if len(sys.argv) > 1:
        inputs = ['../../angle_format_map.json'] + src_files + ['common.h', 'constants.h']
        outputs = ['format_autogen.h', 'compiled/mtl_default_shaders.inc']

        if sys.argv[1] == 'inputs':
            print ','.join(inputs)
        elif sys.argv[1] == 'outputs':
            print ','.join(outputs)
        else:
            print('Invalid script parameters')
            return 1
        return 0

    os.chdir(sys.path[0])

    boilerplate_code = template_header_boilerplate.format(
        script_name=sys.argv[0], copyright_year=datetime.today().year)

    # -------- Generate shader constants -----------
    angle_to_gl = angle_format.load_inverse_table('../../angle_format_map.json')
    shader_formats_autogen = gen_shader_enums_code(angle_to_gl.keys())
    shader_autogen_header = boilerplate_code + shader_formats_autogen

    with open('format_autogen.h', 'wt') as out_file:
        out_file.write(shader_autogen_header)
        out_file.close()

    # -------- Compile shaders -----------
    # boilder plate code
    os.system("echo \"{0}\" > compiled/mtl_default_shaders.inc".format(boilerplate_code))
    os.system(
        'echo "// Compiled binary for Metal default shaders.\n\n" >> compiled/mtl_default_shaders.inc'
    )
    os.system('echo "#include <TargetConditionals.h>\n\n" >> compiled/mtl_default_shaders.inc')

    os.system('echo "// clang-format off" >> compiled/mtl_default_shaders.inc')

    # pre-compiled shaders
    gen_precompiled_shaders(10.13, 11.0, 'compiled_default_metallib', '', src_files)
    gen_precompiled_shaders(10.13, 11.0, 'compiled_default_metallib_debug',
                            '-gline-tables-only -MO', src_files)
    gen_precompiled_shaders(10.14, 12.0, 'compiled_default_metallib_2_1', '', src_files)
    gen_precompiled_shaders(10.14, 12.0, 'compiled_default_metallib_2_1_debug',
                            '-gline-tables-only -MO', src_files)

    os.system('echo "// clang-format on" >> compiled/mtl_default_shaders.inc')


if __name__ == '__main__':
    sys.exit(main())
