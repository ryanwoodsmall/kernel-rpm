%define kmaj 4
%define kmin 9
%define kpat 251
%define kver %{kmaj}.%{kmin}.%{kpat}

Name: kernel
Summary: The Linux Kernel
Version: %{kver}
Release: 1%{?dist}
License: GPL
Group: System Environment/Kernel
Vendor: The Linux Community
URL: http://www.kernel.org
Source0: https://cdn.kernel.org/pub/linux/kernel/v%{kmaj}.x/linux-%{version}.tar.xz
Source1: https://raw.githubusercontent.com/ryanwoodsmall/kernel-rpm/master/rpm/SOURCES/kernel-config-%{kmaj}.%{kmin}
BuildRoot: %{_tmppath}/%{name}-%{PACKAGE_VERSION}-root
Provides:  kernel-%{version} kernel-firmware linux-firmware
%define __spec_install_post /usr/lib/rpm/brp-compress || :
%define debug_package %{nil}

%description
The Linux Kernel, the operating system core itself

%package headers
Summary: Header files for the Linux kernel for use by glibc
Group: Development/System
Obsoletes: kernel-headers
Provides: kernel-headers = %{version}
%description headers
Kernel-headers includes the C header files that specify the interface
between the Linux kernel and userspace libraries and programs.  The
header files define structures and constants that are needed for
building most standard programs and are also needed for rebuilding the
glibc package.

%package devel
Summary: Development package for building kernel modules to match the %{version} kernel
Group: System Environment/Kernel
AutoReqProv: no
%description -n kernel-devel
This package provides kernel headers and makefiles sufficient to build modules
against the %{version} kernel package.

%prep
%setup -q -n linux-%{version}
cp %{SOURCE1} .config
make olddefconfig

%build
make clean && make %{?_smp_mflags}

%install
KBUILD_IMAGE=$(make image_name)
%ifarch ia64
mkdir -p $RPM_BUILD_ROOT/boot/efi $RPM_BUILD_ROOT/lib/modules
%else
mkdir -p $RPM_BUILD_ROOT/boot $RPM_BUILD_ROOT/lib/modules
%endif
mkdir -p $RPM_BUILD_ROOT/lib/firmware/%{version}
INSTALL_MOD_PATH=$RPM_BUILD_ROOT make %{?_smp_mflags} KBUILD_SRC= mod-fw= modules_install
INSTALL_FW_PATH=$RPM_BUILD_ROOT/lib/firmware/%{version}
make INSTALL_FW_PATH=$INSTALL_FW_PATH firmware_install
%ifarch ia64
cp $KBUILD_IMAGE $RPM_BUILD_ROOT/boot/efi/vmlinuz-%{version}
ln -s efi/vmlinuz-%{version} $RPM_BUILD_ROOT/boot/
%else
%ifarch ppc64
cp vmlinux arch/powerpc/boot
cp arch/powerpc/boot/$KBUILD_IMAGE $RPM_BUILD_ROOT/boot/vmlinuz-%{version}
%else
cp $KBUILD_IMAGE $RPM_BUILD_ROOT/boot/vmlinuz-%{version}
%endif
%endif
make %{?_smp_mflags} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr KBUILD_SRC= headers_install
cp System.map $RPM_BUILD_ROOT/boot/System.map-%{version}
cp .config $RPM_BUILD_ROOT/boot/config-%{version}
%ifnarch ppc64
bzip2 -9 --keep vmlinux
mv vmlinux.bz2 $RPM_BUILD_ROOT/boot/vmlinux-%{version}.bz2
%endif
rm -f $RPM_BUILD_ROOT/lib/modules/%{version}/{build,source}
mkdir -p $RPM_BUILD_ROOT/usr/src/kernels/%{version}
EXCLUDES="--exclude SCCS --exclude BitKeeper --exclude .svn --exclude CVS --exclude .pc --exclude .hg --exclude .git --exclude .tmp_versions --exclude=*vmlinux* --exclude=*.o --exclude=*.ko --exclude=*.cmd --exclude=Documentation --exclude=firmware --exclude .config.old --exclude .missing-syscalls.d"
tar $EXCLUDES -cf- . | (cd $RPM_BUILD_ROOT/usr/src/kernels/%{version};tar xvf -)
cd $RPM_BUILD_ROOT/lib/modules/%{version}
ln -sf /usr/src/kernels/%{version} build
ln -sf /usr/src/kernels/%{version} source

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -x /sbin/installkernel -a -r /boot/vmlinuz-%{version} -a -r /boot/System.map-%{version} ]; then
cp /boot/vmlinuz-%{version} /boot/.vmlinuz-%{version}-rpm
cp /boot/System.map-%{version} /boot/.System.map-%{version}-rpm
rm -f /boot/vmlinuz-%{version} /boot/System.map-%{version}
/sbin/installkernel %{version} /boot/.vmlinuz-%{version}-rpm /boot/.System.map-%{version}-rpm
rm -f /boot/.vmlinuz-%{version}-rpm /boot/.System.map-%{version}-rpm
fi
rpm --eval '%{rhel}' | grep -q ^7 && grub2-mkconfig -o /boot/grub2/grub.cfg

%postun
rpm --eval '%{rhel}' | grep -q ^7 && grub2-mkconfig -o /boot/grub2/grub.cfg
# XXX - can't run this since we're not setting an extra version (EXTRAVERSION in Makefile)
# XXX - will remove the initramfs/initrd on same version but different releases upgrade
#test -e /boot/initramfs-%{version}.img && rm -f /boot/initramfs-%{version}.img

%files
%defattr (-, root, root)
/lib/modules/%{version}
%exclude /lib/modules/%{version}/build
%exclude /lib/modules/%{version}/source
/lib/firmware/%{version}
/boot/*

%files headers
%defattr (-, root, root)
/usr/include

%files devel
%defattr (-, root, root)
/usr/src/kernels/%{version}
/lib/modules/%{version}/build
/lib/modules/%{version}/source

