#  Copyright  2019 Alexis Lopez Zubieta
#
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
import os
import stat


class AppRun:
    env = {
        'LD_LIBRARY_DIRS': None,
        'LINKER_PATH': None,
        'XDG_DATA_DIRS': '${APPDIR}/usr/local/share:${APPDIR}/usr/share:${XDG_DATA_DIRS}',
        'XDG_CONFIG_DIRS': '$APPDIR/etc/xdg:$XDG_CONFIG_DIRS',
        'EXEC_ARGS': '$@',
    }
    sections = {
        'HEADER': [
            '#!/bin/bash',
            '# This file was created by AppImageBuilder',
            ''
        ],
        'APPDIR': [
            '# Fallback APPDIR variable setup for uncompressed usage',
            'if [ -z ${APPDIR+x} ]; then',
            '    APPDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"',
            'fi'
        ],
        'EXEC': [
            '# Launch application using only the bundled libraries',
            'exec "${LINKER_PATH}" \\',
            '   --inhibit-cache --library-path "${LD_LIBRARY_DIRS}" \\',
            '  ${APPDIR}/${BIN_PATH} ${EXEC_ARGS}',
            ''
        ]
    }

    def __init__(self, bin_path, exec_args=None):
        assert bin_path

        self.env['BIN_PATH'] = bin_path
        if exec_args:
            self.env['EXEC_ARGS'] = exec_args

    def save(self, path):
        lines = self._generate()

        with  open(path, "w") as f:
            f.write("\n".join(lines))

        self._set_permissions(path)

    def _generate(self):
        file_lines = []
        file_lines.extend(self.sections['HEADER'])
        file_lines.extend(self.sections['APPDIR'])

        file_lines.extend(self._generate_env_section())

        for k, v in self.sections.items():
            if k not in ['HEADER', 'APPDIR', 'EXEC', 'EXEC_ARGS']:
                # avoid including any special section
                file_lines.extend(['', '# %s' % k])
                file_lines.extend(v)

        file_lines.extend(self.sections['EXEC'])

        return file_lines

    def _generate_env_section(self):
        lines = ['', '# Run Environment Setup']
        for k, v in self.env.items():
            if v:
                line = 'export %s="%s"' % (k, v)
                lines.append(line)
        lines.append('')
        return lines

    def _set_permissions(self, path):
        os.chmod(path, stat.S_IRWXU | stat.S_IXGRP | stat.S_IRGRP | stat.S_IXOTH | stat.S_IROTH)
