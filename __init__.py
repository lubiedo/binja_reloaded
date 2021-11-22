from __future__ import print_function
import sys
import os
import watchdog.observers
import watchdog.events
import importlib
from types import ModuleType

plugin_dir = os.path.dirname(os.path.dirname(__file__))


def splitall(path):
    path = path[1:]
    tokens = []
    while True:
        h, t = os.path.split(path)
        if h == '':
            break
        else:
            path = h
            tokens.append(t)
    return tokens[::-1]


class PluginHandler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self):
        super(self.__class__, self).__init__(patterns=['*.py'])
        self._skip = len(splitall(plugin_dir))

    def on_modified(self, event):
        fp = event.src_path
        mod_path = fp[:fp.rfind('.')]
        mod_path = splitall(mod_path)[self._skip:]

        if mod_path[-1] == '__init__':
            mod_path.pop()
        elif mod_path[0] == __name__:
            print('reloaded> Not reloading myself :/')
            return

        # for i in range(len(mod_path)):
        for i in [len(mod_path)-1]:
            mod_name = '.'.join(mod_path[:len(mod_path)-i])

            if mod_name in sys.modules:
                print(f'reloaded> Reloading "{mod_name}"...')
                try:
                    mod = sys.modules[mod_name]
                    for submod_name in mod.__dir__():
                        if submod_name.startswith('__') or \
                           submod_name == 'binaryninja':
                            continue
                        if not isinstance(mod.__dict__[submod_name], ModuleType):
                            continue
                        submod = importlib.import_module(
                            f'.{submod_name}', mod_name
                        )
                        importlib.reload(submod)
                except Exception as e:
                    print(e)
            else:
                print(f'reloaded> Not reloading "{mod_name}"...')


observer = watchdog.observers.Observer()
observer.schedule(PluginHandler(), plugin_dir, recursive=True)
observer.start()
