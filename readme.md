# PhobosExec

Main executive for the phobos rover, responsible for taking commands from the
communications module and then execuiting the right part of the system to deal
with that command.

Currently comms interaction not setup but you can run script files by calling 
the following from this directory.

```bash
python phobos_exec scripts/demo_01.prs
```

This will create a new directory under `sessions/` with a timestamp which will
hold all the output data, logs, and archives from the session.