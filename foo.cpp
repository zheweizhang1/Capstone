#include <iostream>

class Foo{
    public:
        void bar(){
            for(int i = 1; i < 10; i++){
                std::cout << std::endl << i << ". Hello, this C++";
            }
            std::cout << std::endl;
        }
};

extern "C" {
    Foo* Foo_new(){ return new Foo(); }
    void Foo_bar(Foo* foo){ foo->bar(); }
}