#include <stdlib.h>

/* Variability Stub */
int rt_FOO() {
  return getenv("FOO") != NULL;
}

#include <stdio.h>


void func(){
    printf("foo");
}


int main(){
  if(rt_FOO()){
    func();
  }
}