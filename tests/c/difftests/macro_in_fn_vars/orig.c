int main(){
  #ifdef FOO
    int x = 2;
  #endif
  #ifdef FOO
    func(x);
  #endif
}
