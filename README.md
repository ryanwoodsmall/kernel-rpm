# kernel-rpm

kernel spec, config (based on fedora src.rpm) for upstream vanilla kernel rpms from kernel.org

built for and run/tested only on centos 7 x86\_64

# build

for 4.19:

```
mkdir -p ${HOME}/rpmbuild/{SPECS,SOURCES}
curl -kLo ${HOME}/rpmbuild/SPECS/kernel.spec https://raw.githubusercontent.com/ryanwoodsmall/kernel-rpm/master/rpm/SPECS/kernel-4.19.spec
spectool -g -A -R ${HOME}/rpmbuild/SPECS/kernel.spec
( time ( rpmbuild -ba --clean ${HOME}/rpmbuild/SPECS/kernel.spec ) ) 2>&1 | tee /tmp/kernelbuild.out
```

# todo

- detect and generate EFI grub.cfg
  - */boot/efi/EFI/centos/grub.cfg* on default c7
- probably need updated *linux-firmware.spec* from fedora as well
