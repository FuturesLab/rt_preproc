#include <stdio.h>

#ifdef FOO
  void func(){
    printf("foo");
  }
#endif 
 
int main(){
  if ("FOO"){
    func();
  }
  #ifdef FOO
    func();
  #endif
}
