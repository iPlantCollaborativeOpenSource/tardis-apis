# Install Snowflake on Ubuntu 12.04


## Install openjdk-7
~~~~~ bash
apt-get install openjdk-7-jre openjdk-7-jdk
export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64
update-alternatives --config java # choose openjdk-7
update-alternatives --config javac # choose openjdk-7
~~~~~~

## Install ant
~~~~~ bash
  cd /opt
  wget http://www.eng.lsu.edu/mirrors/apache//ant/binaries/apache-ant-1.9.0-bin.tar.gz
  tar xfvz ./apache-ant-1.9.0-bin.tar.gz
  ln -s /opt/apache-ant-1.9.0/bin/ant /usr/local/bin/ant
  export ANT_HOME=/opt/apache-ant-1.9.0
~~~~~

## Install maven
~~~~~ bash
cd /opt
wget http://mirror.cc.columbia.edu/pub/software/apache/maven/maven-3/3.0.5/binaries/apache-maven-3.0.5-bin.tar.gz
tar xfvz ./apache-maven-3.0.5-bin.tar.gz
ln -s /opt/apache-maven-3.0.5/bin/mvn /usr/local/bin/mvn
export M2_HOME=/opt/apache-maven-3.0.5
~~~~~

## Install Thrift
~~~~~ bash
apt-get install libboost-dev libboost-test-dev libboost-program-options-dev libevent-dev automake libtool flex bison pkg-config g++ libssl-dev
apt-get install python-dev python-twisted
apt-get install ruby-full ruby-dev librspec-ruby rubygems libdaemons-ruby libgemplugin-ruby
gem install bundle
apt-get remove rake
gem install bundler
gem install rake
gem install rspec
gem install mongrel --pre
wget http://mirror.metrocast.net/apache/thrift/0.9.0/thrift-0.9.0.tar.gz
tar xfvz ./thrift-0.9.0.tar.gz
cd thrift-0.9.0/
./configure --with-boost=/usr/local
cd ./lib/rb/
bundle install
cd ../..
make
make install
~~~~~

## Install zookeeper
~~~~~ bash
wget http://mirror.metrocast.net/apache/zookeeper/zookeeper-3.4.5/zookeeper-3.4.5.tar.gz
tar xfvz ./zookeeper-3.4.5.tar.gz
cd ./zookeeper-3.4.5
cp conf/zoo_sample.cfg conf/zoo.cfg
cd ./bin
./zkServer.sh start
~~~~~

## Install snowflake
~~~~~ bash
apt-get install git
git clone https://github.com/twitter/snowflake
~~~~~

## Fix snowflake
~~~~~ bash
cd snowflake
Change maven-finagle-thrift-plugin # https://github.com/yourabi/snowflake/commit/1d56336fb8277da22edde75e0fbfc1f37c3c9b66
mvn -U test # won't quite work.
cd $HOME/.m2/repository/org/scala-tools/testing/specs_2.9.2/1.6.9 and download missing specs_2.9.2-1.6.9.jar
wget http://repo.typesafe.com/typesafe/scala-tools-releases-cache/org/scala-tools/testing/specs_2.9.2/1.6.9/specs_2.9.2-1.6.9.jar
mvn clean compile install
~~~~~

# Everything works, just deploy appropriately.

## Horrible Unusable Example:
Export or set $CLASSPATH $JAVA_OPTS $JAVA_HOME in bash environment or hard code.
~~~~~ bash
export MAIN_CLASS=com.twitter.service.snowflake.SnowflakeServer
${JAVA_HOME}/bin/java ${JAVA_OPTS} -cp "/opt/snowflake/target/*:${CLASSPATH}" ${MAIN_CLASS} -f /opt/snowflake/config/development2.scala
cd /opt/snowflake/src/scripts
cp -r ../../target/generated-sources/thrift/gen-rb .
edit ./src/client_test.rb and add $:.push("./gen-rb") before requires.
./client_test.rb 10 localhost:7610 awesome
"localhost"
"7610"
328241381325672448 awesome 1
328241381329866752 awesome 1
328241381334061056 awesome 1
328241381338255360 awesome 1
328241381342449664 awesome 1
328241381342449665 awesome 1
328241381346643968 awesome 1
328241381350838272 awesome 1
328241381355032576 awesome 1
328241381359226880 awesome 1
~~~~~~

## Likely Problems
~~~~~ java
Exception in thread "main" java.lang.NoSuchMethodError: scala.collection.immutable.Map$.apply(Lscala/collection/Seq;)Lscala/collection/GenMap;
        at com.twitter.ostrich.admin.RuntimeEnvironment.<init>(RuntimeEnvironment.scala:55)
        at com.twitter.ostrich.admin.RuntimeEnvironment$.apply(RuntimeEnvironment.scala:33)
        at com.twitter.service.snowflake.SnowflakeServer$.main(SnowflakeServer.scala:29)
        at com.twitter.service.snowflake.SnowflakeServer.main(SnowflakeServer.scala)
~~~~~

This is a classpath problem where ~/.m2/repository/org/scala-lang/scala-library/2.8.x is ahead of ~/.m2/repository/org/scala-lang/scala-library/2.9.x

## References

* https://pods.iplantcollaborative.org/wiki/display/csmgmt/Twitter+Snowflake
* https://github.com/twitter/snowflake/issues
* https://github.com/yourabi/snowflake/commit/1d56336fb8277da22edde75e0fbfc1f37c3c9b66

Good Luck!
