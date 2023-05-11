#include <stdio.h>

#ifdef FOO
  void func(){
    printf("foo");
  }
#endif 
 
int main(){
  #ifdef FOO
    func();
  #endif
}
