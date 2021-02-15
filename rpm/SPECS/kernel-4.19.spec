%define kmaj 4
%define kmin 19
%define kpat 176
%define kver %{kmaj}.%{kmin}.%{kpat}
%define krel 7
%define kversion %{kver}-%{krel}

Name: kernel
Summary: The Linux Kernel
Version: %{kver}
Release: %{krel}%{?dist}
License: GPL
Group: System Environment/Kernel
Vendor: The Linux Community
URL: http://www.kernel.org
Source0: https://cdn.kernel.org/pub/linux/kernel/v%{kmaj}.x/linux-%{version}.tar.xz
Source1: https://raw.githubusercontent.com/ryanwoodsmall/kernel-rpm/master/rpm/SOURCES/kernel-config-%{kmaj}.%{kmin}
BuildRoot: %{_tmppath}/%{name}-%{PACKAGE_VERSION}-root
Provides:  kernel-%{version}
BuildRequires: elfutils-devel
BuildRequires: elfutils-libelf-devel
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
sed -i.ORIG '/^EXTRAVERSION/ s/=/= -%{krel}/g' Makefile
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
INSTALL_MOD_PATH=$RPM_BUILD_ROOT make %{?_smp_mflags} KBUILD_SRC= mod-fw= modules_install
%ifarch ia64
cp $KBUILD_IMAGE $RPM_BUILD_ROOT/boot/efi/vmlinuz-%{kversion}
ln -s efi/vmlinuz-%{kversion} $RPM_BUILD_ROOT/boot/
%else
%ifarch ppc64
cp vmlinux arch/powerpc/boot
cp arch/powerpc/boot/$KBUILD_IMAGE $RPM_BUILD_ROOT/boot/vmlinuz-%{kversion}
%else
cp $KBUILD_IMAGE $RPM_BUILD_ROOT/boot/vmlinuz-%{kversion}
%endif
%endif
make %{?_smp_mflags} INSTALL_HDR_PATH=$RPM_BUILD_ROOT/usr KBUILD_SRC= headers_install
cp System.map $RPM_BUILD_ROOT/boot/System.map-%{kversion}
cp .config $RPM_BUILD_ROOT/boot/config-%{kversion}
%ifnarch ppc64
bzip2 -9 --keep vmlinux
mv vmlinux.bz2 $RPM_BUILD_ROOT/boot/vmlinux-%{kversion}.bz2
%endif
rm -f $RPM_BUILD_ROOT/lib/modules/%{kversion}/{build,source}
mkdir -p $RPM_BUILD_ROOT/usr/src/kernels/%{kversion}
EXCLUDES="--exclude SCCS --exclude BitKeeper --exclude .svn --exclude CVS --exclude .pc --exclude .hg --exclude .git --exclude .tmp_versions --exclude=*vmlinux* --exclude=*.o --exclude=*.ko --exclude=*.cmd --exclude=Documentation --exclude=firmware --exclude .config.old --exclude .missing-syscalls.d"
tar $EXCLUDES -cf- . | (cd $RPM_BUILD_ROOT/usr/src/kernels/%{kversion};tar xvf -)
cd $RPM_BUILD_ROOT/lib/modules/%{kversion}
ln -sf /usr/src/kernels/%{kversion} build
ln -sf /usr/src/kernels/%{kversion} source

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -x /sbin/installkernel -a -r /boot/vmlinuz-%{kversion} -a -r /boot/System.map-%{kversion} ]; then
cp /boot/vmlinuz-%{kversion} /boot/.vmlinuz-%{kversion}-rpm
cp /boot/System.map-%{kversion} /boot/.System.map-%{kversion}-rpm
rm -f /boot/vmlinuz-%{kversion} /boot/System.map-%{kversion}
/sbin/installkernel %{kversion} /boot/.vmlinuz-%{kversion}-rpm /boot/.System.map-%{kversion}-rpm
rm -f /boot/.vmlinuz-%{kversion}-rpm /boot/.System.map-%{kversion}-rpm
fi
if $(rpm --eval '%{rhel}' | grep -q ^7) ; then
test -e /boot/grub2/grub.cfg && grub2-mkconfig -o /boot/grub2/grub.cfg
test -e /boot/efi/EFI/centos/grub.cfg && grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg
fi

%postun
if $(rpm --eval '%{rhel}' | grep -q ^7) ; then
test -e /boot/grub2/grub.cfg && grub2-mkconfig -o /boot/grub2/grub.cfg
test -e /boot/efi/EFI/centos/grub.cfg && grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg
fi
test -e /boot/initramfs-%{kversion}.img && rm -f /boot/initramfs-%{kversion}.img

%files
%defattr (-, root, root)
/lib/modules/%{kversion}
%exclude /lib/modules/%{kversion}/build
%exclude /lib/modules/%{kversion}/source
/boot/*

%files headers
%defattr (-, root, root)
/usr/include

%files devel
%defattr (-, root, root)
/usr/src/kernels/%{kversion}
/lib/modules/%{kversion}/build
/lib/modules/%{kversion}/source

