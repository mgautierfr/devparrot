#    This file is part of DevParrot.
#
#    Author: Matthieu Gautier <matthieu.gautier@devparrot.org>
#
#    DevParrot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    DevParrot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with DevParrot.  If not, see <http://www.gnu.org/licenses/>.
#
#
#    Copyright 2011-2013 Matthieu Gautier


from setuptools import setup, find_packages


setup(name='devparrot',
      version='0.9',
      description="The devparrot editor",
      author="Matthieu Gautier",
      author_email="matthieu.gautier@devparrot.org",
      url="http://devparrot.org",
      classifiers=['Operating System :: POSIX',
                   'Programming Language :: Python',
                   'Topic :: Text Editors :: Integrated Development Environments (IDE)',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
                   'Development Status :: 4 - Beta',
                   'Environment ::X11 Applications',
                   'Intended Audience ::Developers'
                  ],
      packages=find_packages(exclude=['tests'])+['devparrot.commands', 'devparrot.modules'],
      package_data= { 'devparrot.core.ui' : [ 'resources/icon48.png' ],
                      'devparrot' : ['icons/*.png'],
                    },

      # pyxdg and pygments are used for file type detection.
      # Maybe we should remove those strong requirements by using custom algorithm.
      install_requires=['tkinter', 'pyxdg', 'picoparse', 'pygments' 'python-magic','pytest'],
      extras_require = {
         'JEDI'     :   ['jedi'],
         'PYGMENTS' :   ['pygments'],
         'XDG'      :   ['pyxdg'],
         'IMAGE'    :   ['Pillow']
      },
      entry_points = {
        'gui_scripts' : [
            'devparrot = devparrot:main'
        ],
        'devparrot.module' : [
            'project = devparrot.modules.project:Project',
            'documentList = devparrot.modules.documentList:DocumentList',
            'externalTool = devparrot.modules.externalTool:ExternalTool',
            'fileExplorer = devparrot.modules.fileExplorer:FileExplorer [XDG]',
            'textHighlight = devparrot.modules.textHighlight:TextHighlight [PYGMENTS]',
            'jedi = devparrot.modules.jediModule:Jedi [JEDI]',
            'tagExplorer = devparrot.modules.tagExplorer:TagExplorer'
        ]
      }
)

