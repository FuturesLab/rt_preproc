#include <stdio.h>
#include <stdlib.h>

void func(){
  printf("foo");
}

void func2(){
  printf("bar");
}

int rt_FOO() {
  return getenv("FOO") != NULL;
}

int rt_BAR() {
  return getenv("BAR") != NULL;
}

int main(){
  if (rt_FOO()) {
    func();
  }
  if (rt_BAR()){
    func2();
  }
  return 0;
}

